import sys
import os 
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'data'))
from together import Together

from dotenv import load_dotenv
load_dotenv()

from llama_parse import LlamaParse
from llama_index.core import SimpleDirectoryReader
from llama_index.core.node_parser import TokenTextSplitter
from llama_index.core.schema import Document 
import pdb  
import json 
import uuid 
'''
What are we doing: we need to figure out how to create chunks from a document

given a list of chunks, I need to group the chunks 
'''


def return_json_from_chunks(chunks):
    jsons = []
    for chunk in chunks:
        jsons.append()

    pass 

def document_to_json(doc, text_string):
    # returns llama Document into a json with filename, text_body, 
    start_char_idx = doc.start_char_idx
    end_char_idx = doc.end_char_idx
    extra_info = doc.extra_info
    filename = doc.metadata['file_name'] 
    content = text_string
    id = str(uuid.uuid4())
    dictionary = {"filename": filename, "content": content, 'id': id}
    return json.dumps(dictionary)

def retrieve_relevant_parts(text, prompt):
    #TODO: Change the model to something else 
    # uses together ai to extract
    client = Together(api_key=os.environ.get("TOGETHER_API_KEY"))
    response = client.chat.completions.create(
        model='togethercomputer/CodeLlama-34b-Instruct',
        messages=[{"role": "user", "content": f"I will give you subsection of an arvix paper and also a user prompt. Please return through extraction only parts of the subsection that are needed to answer the prompt. If none of the subsection is relevant to answer the query, return an empty string. Subsection: {text} Prompt: {prompt}"}]
    )
    content = response.choices[0].message.content
    #TODO: try returning a list of strings using json 

    print(f"Length of initial block {len(text)} Length of response content {len(content)}")
    print(f"The extracted text is: {content}")
    return content

def return_chunks_from_file(file_path, chunk_token_size: int, prompt):
    '''
    Returns the best chunks from a given document. Returns as a json that contains 
    the chunk string, the file_name, ect. 
    '''
    best_chunk_jsons = []

    parser = LlamaParse(result_type="markdown")
    file_extractor = {".pdf": parser}
    documents = SimpleDirectoryReader(input_files=[file_path], file_extractor=file_extractor).load_data()
    only_document = documents[0]
    
    # get chunks from all the documents 
    text_splitter = TokenTextSplitter(chunk_size=chunk_token_size, chunk_overlap=200)
    chunks = text_splitter.split_text(only_document.text)
    chunk_docs = [Document(text=chunk) for chunk in chunks] 

    for chunk_doc in chunk_docs:
        best_chunk_text = retrieve_relevant_parts(chunk_doc.text, prompt)
        best_chunk_jsons.append(document_to_json(only_document, best_chunk_text))

    return best_chunk_jsons

def driver(folder_path, prompt):
    all_json = []
    for file in os.listdir(folder_path):
        best_jsons = return_chunks_from_file(os.path.join(folder_path, file), 7000, prompt)
        for json_str in best_jsons:
            all_json.append(json.loads(json_str))

    with open("data.json", "w") as file:
        json.dump(all_json, file, indent=4)
    return all_json

if __name__ == "__main__":
    driver('/Users/justin/Desktop/Everything/Code/small_model_moe_rag/data/pdf/', "Tell me about the evaluation dataset used in MetaGPT and compare it against SWE-Bench.")
    #return_chunks_from_file('/Users/justin/Desktop/Everything/Code/small_model_moe_rag/data/pdf/1602_longlora_efficient_fine_tuning.pdf', )

