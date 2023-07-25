from typing import Any
from agents.software_engineer.write_react_native_code import write_code
from aivengers import Agent
import os

class SWEAgent(Agent):
    def __init__(self):
        self.name = "Software Engineer"
        self.description = "Software Engineer"
        self.linear_id = os.getenv("LINEAR_ID_SWE")
        os.environ['LINEAR_API_KEY'] = os.environ['LINEAR_API_KEY_SWE']
        
    # def __init__(self, name, description, linear_id):
    #     super().__init__(name, description, linear_id)
    #     os.environ['LINEAR_API_KEY'] = os.environ['LINEAR_API_KEY_SWE']
        
    async def __call__(self, issue_id: str, project_req: str, uml: str, folder_output: str):
        client = self.init_client()
        await self.start_up_comment(client=client, issue_id=issue_id)
        
        code= write_code(input_prompt=project_req + "\n" + uml + "\nFolder structure: \n" + folder_output, out_file="App.js")
        await self.comment(client=client,body="Generated code: \n```" + code+ '\n```', issue_id=issue_id)