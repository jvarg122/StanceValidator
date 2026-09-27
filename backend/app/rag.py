import tempfile
import uuid
import anthropic
from langchain_community.document_loaders import PyPDFLoader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_postgres import PGVector
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.config import get_settings
from app.models import UploadedDocument

client = anthropic.Anthropic()
settings = get_settings()

_embeddings = None


def get_embeddings():
    global _embeddings
    if _embeddings is None:
        _embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    return _embeddings


def get_vector_store(collection_name):
    return PGVector(
        embeddings=get_embeddings(),
        collection_name=collection_name,
        connection=settings.database_url,
        use_jsonb=True,
    )


def ingest_document(db, file_bytes, filename):
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        tmp.write(file_bytes)
        tmp_path = tmp.name

    loader = PyPDFLoader(tmp_path)
    pages = loader.load()

    splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=80)
    chunks = splitter.split_documents(pages)

    collection_name = f"doc_{uuid.uuid4().hex[:16]}"
    store = get_vector_store(collection_name)
    if chunks:
        store.add_documents(chunks)

    document = UploadedDocument(filename=filename, collection_name=collection_name)
    db.add(document)
    db.commit()
    db.refresh(document)

    return document


def retrieve_relevant_chunks(document, query_text, k=5):
    store = get_vector_store(document.collection_name)
    return store.similarity_search(query_text, k=k)


def judge_chunk(sub_claim_text, chunk_text, filename):
    prompt = f"""Sub-claim: {sub_claim_text}

Excerpt from an uploaded document ("{filename}"):
{chunk_text}

Does this excerpt support or conflict with the sub-claim, or is it not actually relevant?
Reply on one line in this exact format:
supports or conflicts or not_relevant | one sentence summary of what the excerpt actually says about the sub-claim | a short direct quote from the excerpt backing that summary"""

    try:
        response = client.messages.create(
            model=settings.model_name,
            max_tokens=300,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = response.content[0].text.strip()
    except Exception:
        return None

    parts = [p.strip() for p in raw.split("|", 2)]
    if len(parts) != 3 or not parts[2]:
        return None

    relation = parts[0].strip("* ").lower()
    if "not_relevant" in relation or "not relevant" in relation:
        return None
    if "conflict" in relation:
        relation = "conflicts"
    elif "support" in relation:
        relation = "supports"
    else:
        return None

    return {
        "url": f"upload://{filename}",
        "relation": relation,
        "summary": parts[1],
        "supporting_quote": parts[2],
        "credibility_score": 0.3,
        "source_type": "user_uploaded",
    }
