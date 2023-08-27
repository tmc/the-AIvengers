from typing import Any
from agents.software_engineer.write_react_native_code import write_code
from aivengers import Agent
import os
from linear_client import LinearClient

class SWEAgent(Agent):
    def __init__(self):
        self.name = "swe"
        self.description = "Software Engineer"
        self.linear_id = os.getenv("LINEAR_ID_SWE")
        os.environ['LINEAR_API_KEY'] = os.environ['LINEAR_API_KEY_SWE']

    async def assign_to_deployment_agent(self, client: LinearClient, issue_id: str):
        deployment_id = os.getenv("LINEAR_ID_PM")
        if not deployment_id:
            raise Exception("Deployment ID not found")
        await client.assign_issue(issue_id=issue_id, assignee_id=deployment_id)
        
        
    async def __call__(self, issue_id: str, project_req: str, uml: str, folder_output: str, filename: str = 'App.js'):
        client = self.init_client()
        await self.start_up_comment(client=client, issue_id=issue_id)
        
        code= write_code(project_reqs=project_req, uml=uml, structure=folder_output, out_file=filename)
        await self.comment(client=client,body=f"Generated code: \n{filename}\n```\n" + code+ '\n```', issue_id=issue_id)

        # Assign to deployment agent!
        await self.assign_to_deployment_agent(client, issue_id)