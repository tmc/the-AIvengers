# hackathon templates - fastapi backend - main.py

from aivengers import Agent
import os
import openai
import json
from fastapi import FastAPI, Request

from dotenv import load_dotenv
from agents.architect.agent import ArchitectAgent
from agents.software_engineer.agent import SWEAgent
from agents.deployment_agent.agent import DeploymentAgent

load_dotenv()

app = FastAPI()


AGENTS = {
    "oracle": Agent(name="oracle", description="Oracle that oversees the project", linear_id=os.getenv("LINEAR_ID_ORACLE")),
    "pm": Agent(name="pm", description="Product Manager", linear_id=os.getenv("LINEAR_ID_PM")),
    "architect": ArchitectAgent(),
    "swe": SWEAgent(),
    "deployment": DeploymentAgent(),
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
    print("payload:", json.dumps(payload, indent=2))
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
        title = j["data"]["title"]
        description = j["data"]["description"]
        # initial_event_completion = await perform_initial_event_completion(payload)
        # print("initial event completion:", initial_event_completion)

        # current: invoke based on assigneeId - future: invoke based on oracle
        if assignee_id == AGENTS["architect"].linear_id: 
            architect_agent = ArchitectAgent()

            # for demo keep the architecture simple TODO: remove this
            demo_architecture_restriction = "Include all the code only in App.js. Do not have multiple files."
            description += "\n" + demo_architecture_restriction

            uml, folder_output = await architect_agent(project_req=title + "\n" + description, 
                                                       issue_id=issue_id)
            print('completed uml and folder_output')
            swe_agent = SWEAgent()
            await swe_agent(issue_id=issue_id, project_req=title + "\n" + description, uml=uml, folder_output=folder_output)
            
            print("starting deployment ...")
            deployment_agent = DeploymentAgent()
            await deployment_agent(issue_id=issue_id, project_name=title)

        
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
