# hackathon templates - fastapi backend - main.py

import os
import openai
from fastapi import FastAPI, Request

from dotenv import load_dotenv
load_dotenv()

openai.api_key = os.environ.get("OPENAI_API_KEY")

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
    webhook_result = await handle_incoming_webhook(j)

    print(webhook_result)
    return {"status": "ok"}


async def handle_incoming_webhook(payload: dict):
    """
    Handle incoming webhook from Linear
    """
    print("handle_incoming_webhook")
    print("payload:", payload)

    # create a chat completion
    initial_event_completion = await perform_initial_event_completion(payload)
    print("initial event completion:", initial_event_completion)


# ORACLE_SYSTEM_PROMPT = """
# """
ORACLE_FUNCTIONS = [
    {
        "name": "assign_to",
        "description": "Assign this issue to another team member.",
        "parameters": {
            {
                "name": "assignee",
                "description": "The team member to assign this issue to.",
                "type": "string",
                "required": True,
                "enum": ["pm", "architect", "swe"],
            }
        ]
    }
]
async def perform_initial_event_completion(payload: dict):
    messages = []
    messages.append({"role": "system", "content": "Don't make assumptions about what values to plug into functions. Ask for clarification if a user request is ambiguous."})
    messages.append({"role": "user", "content": f"""what should we do with this Linear issue:
```
{payload}
```
"""})
    chat_completion = openai.ChatCompletion.create(model="gpt-4", messages=messages, functions=ORACLE_FUNCTIONS)
    # print the chat completion
    print(chat_completion.choices[0].message.content)
    return chat_completion.choices[0].message.content


