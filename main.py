from fastapi import FastAPI

app = FastAPI("Risk Assessment")

@app.get("/")
def read_root():
    return {"Hello": "World"}
