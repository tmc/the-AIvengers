# hackathon templates - fastapi backend - main.py

from fastapi import FastAPI, Request

# dotenv:
from dotenv import load_dotenv
load_dotenv()

app = FastAPI()

from aivengers import Agent

AGENTS = {
    "oracle": Agent(name="pm", description="Product Manager"),
    "pm": Agent(name="pm", description="Product Manager"),
    "architect": Agent(name="architect", description="Architect"),
    "swe": Agent(name="swe", description="Software Engineer"),
}

@app.post("/webhooks/linear")
async def webhooks_linear(request: Request):
    j = await request.json()
    webhook_result = handle_incoming_webhook(j)

    print(webhook_result)
    return {"status": "ok"}








async def handle_incoming_webhook(payload: dict):
    """
    Handle incoming webhook from Linear
    """
    print("handle_incoming_webhook")

