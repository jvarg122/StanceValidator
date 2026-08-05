from fastapi import FastAPI
app = FastAPI()


@app.get("/status")
def health_check():
    return {"status": "ok"}
