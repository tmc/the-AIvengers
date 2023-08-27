from typing import Any
from agents.software_engineer.write_react_native_code import write_code
from aivengers import Agent
import os
import subprocess
from linear_client import LinearClient

class DeploymentAgent(Agent):
    def __init__(self):
        self.name = "deployment_agent"
        self.description = "Deployment Agent"
        self.linear_id = os.getenv("LINEAR_ID_PM")
        os.environ['LINEAR_API_KEY'] = os.environ['LINEAR_API_KEY_PM']
    
    def call_node_script(self, project_name):
        try:
            # Replace 'node' with the correct path to your node executable if necessary
            command = ['node', 'send_code_to_expo.js', project_name]

            # Run the Node.js script and capture its output
            result = subprocess.run(command, capture_output=True, text=True, check=True)

            # Extract the Snack URL from the output
            output_lines = result.stdout.splitlines()
            snack_url = output_lines[-1] if output_lines else None

            return snack_url.strip() if snack_url else "None"
        except subprocess.CalledProcessError as e:
            print("Error calling the Node.js script:", e)
            return "None"
        

        
    async def __call__(self, issue_id: str, project_name: str = "snack", filename: str = 'App.js'):
        print("DeploymentAgent called")
        client = self.init_client()
        await self.start_up_comment(client=client, issue_id=issue_id)

        # get url
        url = self.call_node_script(project_name)

        await self.comment(client=client,body=f"Deployed the project \""+project_name+"\"under: "+url, issue_id=issue_id)