# hackathon templates - fastapi backend - main.py
import os
import openai
import json
from fastapi import FastAPI, Request
from dotenv import load_dotenv
from fastapi-backend.agent.software_engineer import write_code


load_dotenv()
openai.api_key = os.environ.get("OPENAI_API_KEY")
app = FastAPI()
from aivengers import Agent
AGENTS = {
    "pm": Agent(name="pm", description="Product Manager",
        id="d8d188d6-4fef-4567-8aa0-ce3e3a163f9e",
    ),
    "architect": Agent(name="architect", description="Architect"),
    "swe": Agent(name="swe", description="Software Engineer"),
}
@app.post("/webhooks/linear")
async def webhooks_linear(request: Request):
    j = await request.json()
    webhook_result = await handle_incoming_webhook(j)
    print(webhook_result)
    return {"status": "ok"}


# Software Engineer Agent
import langchain
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from langchain.llms import OpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
import re


prompt_template = '''
You are an expert in javascript, you will implement an App according to engineer leader's requirements:
{dev_requirements}

Constraints:
- Please only use javascript syntax and react-native API, don't use any other libraries
- only reply code, don't reply any other text

// Your javascript code here:
'''

# llm = OpenAI(temperature=0.9, model_name='gpt-3.5-turbo-0613')
llm = OpenAI(temperature=0.9, model_name='gpt-4')

def extract_code(string):
    pattern = r'```(jsx|javascript)\s+(.*?)\s+```'
    matches = re.findall(pattern, string, re.DOTALL)
    if matches:
        code_blocks = [match[1] for match in matches]
        return "\n".join(code_blocks)
    else:
        return string

class CodeRequest(BaseModel):
    input_prompt: str
    out_file: Optional[str] = None

class CodeResponse(BaseModel):
    code: str

@app.post("/write_code/", response_model=CodeResponse)
def write_code_endpoint(request: CodeRequest):
    prompt = PromptTemplate.from_template(prompt_template)
    chain = LLMChain(llm=llm, prompt=prompt)
    generated_code = chain.run(dev_requirements=request.input_prompt)
    # request.input_prompt
    # generated_code = llm.predict()
    extracted_code = extract_code(generated_code)

    if request.out_file:
        with open(request.out_file, 'w') as f:
            f.write(extracted_code)

    return {"code": extracted_code}


##
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
    is_assigned_to_pm = j["data"]["assigneeId"] == AGENTS["pm"].id
    if is_assigned_to_pm:
        # TODO: invoke pm agent
        response = write_code_endpoint()
        return response
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