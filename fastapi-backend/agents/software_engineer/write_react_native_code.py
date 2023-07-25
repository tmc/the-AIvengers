import argparse
from langchain.chat_models import ChatOpenAI
import re

prompt = '''
Simple visualization app using react native code:
1. Visualize these images in row by row, max width is 500px: 
- https://images.unsplash.com/photo-1682685796965-9814afcbff55
- https://images.unsplash.com/photo-1661956601349-f61c959a8fd4
2. Add title "AIvenger demo show"
3. Write "Hello world" as body texts
4. Add a button "Click me" at the bottom, when click, it will hide/unhide all images

Constraints:
- Please only use javascript syntax and react-native API, don't use any other libraries
- only reply code, don't reply any other text

// Your javascript code here:
'''

llm = ChatOpenAI(temperature=0.9, model_name='gpt-3.5-turbo-0613')

def extract_code(string):
    pattern = r'```javascript\s+(.*?)\s+```'
    match = re.search(pattern, string, re.DOTALL)
    if match:
        code = match.group(1)
        return code
    else:
        return string

def write_code(input_prompt=prompt, out_file=None):
    res = llm.predict(input_prompt)
    extracted_code = extract_code(res)

    if out_file:
        with open(out_file, 'w') as f:
            f.write(extracted_code)

    return extracted_code

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate code using OpenAI language model and optionally save it to a file.')
    parser.add_argument('--out_file', type=str, default=None, help='Output file path to save the generated code.')
    args = parser.parse_args()

    generated_code = write_code(out_file=args.out_file)

    if not args.out_file:
        print(generated_code)
