# hackathon templates - fastapi backend - main.py

from fastapi import FastAPI
from agents.architect import folder_structure_gen, codegen, generate_uml_code

app = FastAPI()

@app.get("/")
async def root():
    
    return {"message": "Hello World"}

