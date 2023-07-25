import langchain
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
import re

app = FastAPI()

prompt_template = '''
You are an expert in javascript, you will implement an App according to engineer leader's requirements:
{dev_requirements}

Constraints:
- Please only use javascript syntax and react-native API, don't use any other libraries
- only reply code, don't reply any other text

// Your javascript code here:
'''

# llm = OpenAI(temperature=0.9, model_name='gpt-3.5-turbo-0613')
llm = ChatOpenAI(temperature=0.9, model_name='gpt-4')

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
