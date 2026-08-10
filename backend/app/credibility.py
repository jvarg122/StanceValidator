from urllib.parse import urlparse

HIGH_TRUST_DOMAINS = {".gov", ".edu"}
ACADEMIC_DOMAINS = {
    "semanticscholar.org",
    "ncbi.nlm.nih.gov",
    "doi.org",
    "nature.com",
    "sciencedirect.com",
    "arxiv.org",
}


def score_source(url):
    domain = urlparse(url).netloc.lower()

    if any(domain.endswith(suffix) for suffix in HIGH_TRUST_DOMAINS):
        return 0.9
    if any(academic in domain for academic in ACADEMIC_DOMAINS):
        return 0.85
    if domain.endswith(".org"):
        return 0.6
    return 0.4
