import json
from plantuml import PlantUML
from typing import Dict
from agents.architect.gpt import GPTInstance
from agents.architect.examples import uml_examples, folder_examples
from linear_client import LinearClient
from aivengers import Agent
import os


PLANT_UML_SERVER = PlantUML(url="http://www.plantuml.com/plantuml/img/")


class ArchitectAgent(Agent):
    def __init__(self):
        self.name = "architect"
        self.description = "Software Architect"
        self.linear_id = os.getenv("LINEAR_ID_ARCHITECT")
        
        os.environ['LINEAR_API_KEY'] = os.getenv(
            "LINEAR_API_KEY_ARCHITECT", os.environ['LINEAR_API_KEY'])

    def process_uml_code(self, uml_code: str) -> str:
        return PLANT_UML_SERVER.get_url(uml_code)

    def generate_uml_code(
        self,
        project_requirements: str, framework_lang: str, framework_ts: str,
        # framework_db: str, framework_int: str,
        max_retries: int = 3
    ) -> Dict:
        print("generate_uml_code")
        print(project_requirements)

        FALLBACK_ERROR_MESSAGE = {
            "url": None,
            "comments": "I'm afraid I cannot generate a diagram at the moment. Please try again",
        }

        uml_agent = GPTInstance(
            functions=[
                {
                    "name": "submit_plantuml_code",
                    "description": "Submit the plant UML code based on the project requirements",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "plantuml_code": {
                                "type": "string",
                                "description": "The plantUML code to submit",
                            },
                            "context_and_reasoning": {
                                "type": "string",
                                "description": "The context and reasoning necessary for the user to understand the UML",
                            },
                        },
                        "required": ["plantuml_code", "context_and_reasoning"],
                    },
                }
            ]
        )
        uml_agent.messages += uml_examples

        retries = 0
        while retries < max_retries:

            try:
                output = uml_agent(
                    f"""I want to brainstorm for a new project, the idea is:\n{project_requirements}.
                    These are some developer's technology preference to include, but keep in mind this is only a preference, do not include it or use it if it doesn't make sense:\n
                        1. preferred programming language = {framework_lang} \n
                        2. preferred tech stack = {framework_ts} \n

                    Can you create an initial diagram (using plantUML) of how I can build it?
                    """
                )

                function_call = output.get("function_call", None)

                if function_call is None:
                    retries += 1
                    uml_agent.logger.warning(
                        "ChatGPT response unsuficient. Retrying...")
                    continue

                if function_call["name"] != "submit_plantuml_code":
                    retries += 1
                    uml_agent.logger.warning(
                        "ChatGPT response unsuficient. Retrying...")
                    continue
                else:
                    arguments = function_call["arguments"]
                    arguments = json.loads(arguments)

                    uml_code = arguments["plantuml_code"]
                    url = self.process_uml_code(uml_code)

                    return {
                        "url": url,
                        "uml_code": uml_code,
                        "comments": arguments["context_and_reasoning"],
                    }

            except json.JSONDecodeError as e:
                retries += 1
                uml_agent.logger.warning(
                    "ChatGPT response unsuficient. Retrying...")
                pass

        return FALLBACK_ERROR_MESSAGE

    def codegen(self, problem_description: str, uml_code: str) -> str:
        folder_structure_agent = GPTInstance(
            system_prompt="Given a UML diagram and problem description, generate the folder structure, include explicit names for the repo to implement it",
            functions=[
                {
                    "name": "submit_folder_structure",
                    "description": "Submit the the folder structure associated with the project",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "folder_structure": {
                                "type": "string",
                                "description": "JSON String where each folder is a key and values might be other dictionaries or strings if a file",
                            },
                        },
                        "required": ["folder_structure"],
                    },
                }
            ],
        )
        output = folder_structure_agent(
            f"Problem description:\n{problem_description}\n UML:\n{uml_code}"
        )

        print(output)

        function_call = output.get("function_call", None)

        if function_call is None:
            return None

        if function_call["name"] != "submit_folder_structure":
            return None
        else:
            arguments = function_call["arguments"]
            arguments = json.loads(arguments)

            return arguments

    def folder_structure_gen(self, problem_description: str, uml_code: str, max_retries: int = 3) -> str:
        FALLBACK_ERROR_MESSAGE = {
            "url": None,
            "comments": "I'm afraid I cannot generate a file directory at the moment. Please try again",
        }

        codegen_agent = GPTInstance(
            system_prompt="You are a helpful assistant.",
            functions=[
                {
                    "name": "submit_file_structure",
                    "description": "Submit the the folder structure associated with the project",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "file_structure": {
                                "type": "string",
                                "description": "JSON String containing all the folders and files",
                            },
                        },
                        "required": ["file_structure"],
                    },
                }
            ],
        )

        codegen_agent.messages += folder_examples

        retries = 0

        while retries < max_retries:
            try:
                output = codegen_agent(
                    f"Help me come up with the organization for the code repository of my project.\nThe problem is {problem_description}.\n"
                    f"The architecture diagram is as follows: {uml_code}"
                )

                print(output)

                function_call = output.get("function_call", None)

                if function_call is None:
                    retries += 1
                    codegen_agent.logger.warning(
                        "ChatGPT response unsuficient. Retrying...")
                    continue

                if function_call["name"] != "submit_file_structure":
                    retries += 1
                    codegen_agent.logger.warning(
                        "ChatGPT response unsuficient. Retrying...")
                    continue
                else:
                    arguments = function_call["arguments"]
                    out_folder = json.loads(arguments)
                    folder_structure = out_folder["file_structure"]
                    return folder_structure
            except json.JSONDecodeError as e:
                retries += 1
                codegen_agent.logger.warning(
                    "ChatGPT response unsuficient. Retrying...")
                pass

        return FALLBACK_ERROR_MESSAGE

   
        
    async def assign_to_swe(self, client: LinearClient, issue_id: str):
        swe_id = os.getenv("LINEAR_ID_SWE")
        if not swe_id:
            raise Exception("SWE ID not found")
        await client.assign_issue(issue_id=issue_id, assignee_id=swe_id)


    async def __call__(self, issue_id, project_req, framework_lang="js", framework_ts="react native"):
        client = self.init_client()
        await self.start_up_comment(client, issue_id)
        
        output = self.generate_uml_code(project_requirements=project_req,
                                        framework_lang=framework_lang, framework_ts=framework_ts
                                        )
        uml_code = output.get("uml_code")
        await self.comment(client=client,
                body="Generated UML diagram: " + output['url'] + "\n" + output.get("comments"),
                issue_id=issue_id,
            )

        folder_output = None

        if uml_code:
            print('generating file structure')
            folder_output = self.codegen(problem_description=project_req,
                                         uml_code=uml_code)
            await self.comment(client=client,
                    body="generated folder structure: " + '\n```\n' + folder_output.__str__() +
                    '\n```',
                    issue_id=issue_id,
                    # parent_id=None,
                )
            print(folder_output)

        await self.comment(client=client,body="Done",issue_id=issue_id)
        
        # TODO: call the swe/oracle agent
        await self.assign_to_swe(client, issue_id)

        return uml_code, folder_output
