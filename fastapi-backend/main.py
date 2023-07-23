# hackathon templates - fastapi backend - main.py

import os
import openai
import json
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
    print("payload:", json.dumps(payload))
    j = payload

    is_update = j["action"] == "update"
    is_create = j["action"] == "create"
    assignee_changed = "assigneeId" in j.get("updatedFrom", {})
    status_changed = "stateId" in j.get("updatedFrom", {})

    # initial_event_completion = await perform_initial_event_completion(payload)
    # print("initial event completion:", initial_event_completion)

    # TODO: determine which agent to invoke
    return None


ORACLE_FUNCTIONS = [
    {
        "name": "assign_to",
        "description": "Assign this issue to another team member.",
        "parameters": {
            "type": "object",
            "properties": {
                "assignee": {
                    "description": "The team member to assign this issue to.",
                    "type": "string",
                    "enum": ["pm", "architect", "swe"],
                }
            }
        }
    }
]

async def perform_initial_event_completion(payload: dict):
    messages = []
    messages.append({"role": "system", "content": """Don't make assumptions about what values to plug into functions.

The following assignee values are valid: pm, architect, swe."""})
    messages.append({"role": "user", "content": f"""Here is the linear issue in JSON form:
```{payload}```

if this issue seems like it should be reassigned please do so."""})
    print(messages)
    chat_completion = openai.ChatCompletion.create(model="gpt-4", messages=messages, functions=ORACLE_FUNCTIONS)
    # print the chat completion
    print(json.dumps(chat_completion.choices[0].message.content))

    # TODO:
    # look for function calls in the chat completion, and if there are any, call the function.

    return chat_completion.choices[0].message.content


