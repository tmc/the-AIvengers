# hackathon templates - fastapi backend - main.py

from fastapi import FastAPI

# dotenv:
from dotenv import load_dotenv
load_dotenv()

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}
