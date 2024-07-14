import subprocess
import sys
import os
import json 
from dotenv import load_dotenv
load_dotenv()
#api_key = os.getenv("OPENAI_API_KEY")

def run_command(command, is_typescript=False):
    try:
        result = subprocess.run(command, check=True, text=True, capture_output=True)
        if is_typescript:
            return result.stdout
        else: 
            return True
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}", file=sys.stderr)
        print(f"Error output: {e.stderr}", file=sys.stderr)
        return False

import subprocess
import shlex

def run_command_with_live_output(command):
    # Split the command if it's a string
    if isinstance(command, str):
        command = shlex.split(command)
    
    # Start the process
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,  # Redirect stderr to stdout
        text=True,
        bufsize=1,
        universal_newlines=True
    )
    
    # Read and print output in real-time
    for line in process.stdout:
        print(line, end='')  # end='' to avoid double line breaks
    
    # Wait for the process to complete and get the return code
    return_code = process.wait()
    
    if return_code != 0:
        raise subprocess.CalledProcessError(return_code, command)
    



def run_python_script(script_path, folder_path, prompt):
    print(f"Executing Python script: {script_path}")
    command = [sys.executable, script_path, folder_path, prompt]
    return run_command(command)

def run_typescript_script(script_path, question, json_file):
    print(f"Executing TypeScript script: {script_path}")
    command = ["npx", "tsx", script_path, question, json_file]
    return run_command(command, True)

def orchestrate(pdf_folder_path, prompt, ts_script_path, json_file):
    # Run the Python script
    if True:
    #if run_python_script("/Users/justin/Desktop/Everything/Code/small_model_moe_rag/retriever/main.py", pdf_folder_path, prompt):
        # If Python script succeeds, run the TypeScript script
        output_ids = run_typescript_script(ts_script_path, prompt, json_file)
        output_msgs = get_text_from_ids(output_ids)
        print(f"rag retrieval list: {output_msgs}")

        response = answer_question(output_msgs, prompt)
        print(f"Question: {prompt} Answer:{response}")   


def answer_question(context_list, prompt):
    from openai import OpenAI
    client = OpenAI()

    response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {
        "role": "system",
        "content": [
            {
            "type": "text",
            "text": f"You are a question answering bot. Please answer the following question: {prompt}\nUse the following context to answer your question: {context_list}"
            }
        ]
        }
    ],
    temperature=1,
    max_tokens=256,
    top_p=1,
    frequency_penalty=0,
    presence_penalty=0
    )

    return response.choices[0].message.content 

def get_text_from_ids(output_ids, json_file="data.json"):
    with open(json_file, 'r') as file:
        data = json.load(file)

    ret_list = [obj['content'] for obj in data if obj['id'] in output_ids]
    return ret_list

if __name__ == "__main__":
    pdf_folder = 'C:\\Users\\tobia\\Downloads\\llama-index-pdf'


    # if number == 0:
#       prompt = "What dataset is used to train the model."
#       json_file = "data.json"  # This is the file created by your Python script
#   elif number == 1:
#       prompt = "Tell me about the evaluation dataset used in MetaGPT and compare it against SWE-Bench."
#       json_file = "question_one.json"  # This is the file created by your Python script
#   elif number == 2:
#       prompt = "What is the exact improvement in ROUGE-1 score that LoftQ achieves over QLoRA for the XSum dataset using 4-bit NF4 quantization with rank 16?"
#       json_file = "question_five.json"  # This is the file created by your Python script
#   elif number == 3:
#       prompt = "What is the perplexity score for LoftQ on LLAMA-2-13b using 2-bit quantization on the WikiText-2 dataset?"
#       json_file = "question_six.json"  # This is the file created by your Python script
#   else:
#       prompt = "Knowledge card Top-down exp improves Codex by how much in the Generate GKP Model for STEM?"
#       json_file = "question_seven.json"  # This is the file created by your Python script

    print("""
    0: What dataset is used to train the model.
    1: Tell me about the evaluation dataset used in MetaGPT and compare it against SWE-Bench.
    2: What is the exact improvement in ROUGE-1 score that LoftQ achieves over QLoRA for the XSum dataset using 4-bit NF4 quantization with rank 16?
    3: What is the perplexity score for LoftQ on LLAMA-2-13b using 2-bit quantization on the WikiText-2 dataset?
    4: Knowledge card Top-down exp improves Codex by how much in the Generate GKP Model for STEM?
""")



    # Read number from CLI
    number = int(input("Choose a question: "))



    if number == 0:
        prompt = "What dataset is used to train the model."
        json_file = "data.json"  # This is the file created by your Python script
    elif number == 1:
        prompt = "Tell me about the evaluation dataset used in MetaGPT and compare it against SWE-Bench."
        json_file = "question_one.json"  # This is the file created by your Python script
    elif number == 2:
        prompt = "What is the exact improvement in ROUGE-1 score that LoftQ achieves over QLoRA for the XSum dataset using 4-bit NF4 quantization with rank 16?"
        json_file = "question_five.json"  # This is the file created by your Python script
    elif number == 3:
        prompt = "What is the perplexity score for LoftQ on LLAMA-2-13b using 2-bit quantization on the WikiText-2 dataset?"
        json_file = "question_six.json"  # This is the file created by your Python script
    else:
        prompt = "Knowledge card Top-down exp improves Codex by how much in the Generate GKP Model for STEM?"
        json_file = "question_seven.json"  # This is the file created by your Python script

    print(f"Processing query: {prompt}")

    ts_script = "/Users/justin/Desktop/Everything/Code/small_model_moe_rag/resolver/main.ts"

    orchestrate(pdf_folder, prompt, ts_script, json_file)