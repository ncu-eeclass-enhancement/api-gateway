from fastapi import FastAPI

app = FastAPI()

@app.get("/", status_code=204)
def root():
    return None
