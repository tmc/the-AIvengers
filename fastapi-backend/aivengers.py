from dataclasses import dataclass
from linear_types import (
    CommentCreateInput,
)
from linear_client import LinearClient

@dataclass
class Agent:
    name: str
    description: str
    linear_id: str = None
    
    def init_client(self):
        client = LinearClient(endpoint="https://api.linear.app/graphql")
        return client
        

    async def comment(self, client: LinearClient, issue_id: str, body: str):
        await client.create_comment(CommentCreateInput(body=body, issue_id=issue_id))
        
    async def start_up_comment(self, client: LinearClient, issue_id: str):
        await self.comment(client, issue_id, "Starting " + self.name + " agent")
        
        
        
        
        