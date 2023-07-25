# hackathon templates - fastapi backend - main.py

from aivengers import Agent
import os
import openai
import json
from fastapi import FastAPI, Request

from dotenv import load_dotenv
from agents.architect import ArchitectAgent


load_dotenv()

app = FastAPI()


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
    print("is_update:", is_update)
    print("is_create:", is_create)
    print("assignee_changed:", assignee_changed)
    print("status_changed:", status_changed)

    if assignee_changed:
        assignee_id = j["data"].get("assigneeId")
        issue_id = j["data"]["team"]["key"] + "-" + str(j["data"]["number"])
        print("issue_id:", issue_id)
        title = j["data"]["title"]
        description = j["data"]["description"]
        print("title:", title)
        print("description:", description)
        initial_event_completion = await perform_initial_event_completion(payload)
        print("initial event completion:", initial_event_completion)

        # current: invoke based on assigneeId - future: invoke based on oracle
        if assignee_id == "5a9ee6b8-acbd-4142-9ab9-8a9c3f5daf27":  # architect id
            uml, folder_output = await ArchitectAgent(issue_id=issue_id)(project_req=title + "\n" + description, issue_id=issue_id)
            print("uml:", uml)
            print("folder_output:", folder_output)

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
    chat_completion = openai.ChatCompletion.create(
        model="gpt-4", messages=messages, functions=ORACLE_FUNCTIONS)
    # print the chat completion
    message = chat_completion.choices[0].message
    print(json.dumps(message.content))

    if message.get("function_call"):
        function_output = message["function_call"]["arguments"]
        print(function_output)
        return function_output
        
    return chat_completion.choices[0].message.content
