# hackathon templates - fastapi backend - main.py

from fastapi import FastAPI

# dotenv:
from dotenv import load_dotenv
load_dotenv()

app = FastAPI()

@app.get("/webhooks/linear")
async def root():
    return {"message": "Hello World"}
