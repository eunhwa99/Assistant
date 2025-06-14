# from dotenv import load_dotenv
# load_dotenv()

import streamlit as st
from llama_cpp import Llama

llm = Llama(
      model_path="Llama-3.2-3B-Instruct-Q5_K_L.gguf",
      # n_gpu_layers=-1, # Uncomment to use GPU acceleration
      # seed=1337, # Uncomment to set a specific seed
      # n_ctx=2048, # Uncomment to increase the context window
)
st.title("🦜🔗 My first AI App")

def generate_response(input_text):

    prompt = (
        "<|start_header_id|>system<|end_header_id|>\n\n"
        "You are a helpful assistant.\n"
        "<|eot_id|>"
        "<|start_header_id|>user<|end_header_id|>\n\n"
        f"{input_text}"
        "<|eot_id|>"
        "<|start_header_id|>assistant<|end_header_id|>\n\n"
    )
    response = llm.create_completion(
        prompt=prompt,
        max_tokens=5000,
        temperature=0.2,
    )
    print(response)
    st.info(response['choices'][0]['text'])
    


with st.form("my_form"):
    text = st.text_area(
        "Enter text:",
        "What are the three key pieces of advice for learning how to code?",
    )
    submitted = st.form_submit_button("Submit")
    if submitted:
        generate_response(text)