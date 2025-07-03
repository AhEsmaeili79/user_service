from fastapi import FastAPI

app = FastAPI()

@app.get("/test")
def read_root():
    return {"Test": "OK"} 