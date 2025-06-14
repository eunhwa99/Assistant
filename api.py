from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import json
from pyvis.network import Network
from llama_cpp import Llama
import re

app = FastAPI()

# Allow frontend to call API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

llm = Llama(
      model_path="Llama-3.2-3B-Instruct-Q5_K_L.gguf",
      # n_gpu_layers=-1, # Uncomment to use GPU acceleration
      # seed=1337, # Uncomment to set a specific seed
      # n_ctx=2048, # Uncomment to increase the context window
)

def extract_json(response_text):
    # 1) ```로 둘러싸인 코드블록 탐색
    code_blocks = re.findall(r"```(json)?\n(.+?)```", response_text, re.DOTALL)
    if code_blocks:
        json_str = code_blocks[0][1]  # 첫 번째 코드블록 내부 텍스트
        return json.loads(json_str)

    # 2) 코드블록 없으면 { ... } 형태만 추출 시도
    match = re.search(r"\{.*\}", response_text, re.DOTALL)
    if match:
        json_str = match.group(0)
        print(f"Extracted JSON: {json_str}")
        return json.loads(json_str)

    raise ValueError("응답에서 JSON을 찾지 못했습니다.")


class TextInput(BaseModel):
    text: str

@app.post("/api/generate_graph")
async def concept_map(data: TextInput):
    prompt = (
        "<|start_header_id|>system<|end_header_id|>\n\n"
        """You are an expert in summarizing academic papers.
        Your task is to analyze the provided paper text and generate a valid JSON representation of the key concepts and their relationships.
        Do not include any explanation or extra text
        The output should be in the following format:
        {
            "nodes": [
                {"id": "Concept1", "label": "Concept1 description"},
                    ...
                {"id": "ConceptN", "label": "ConceptN description"}],
            "edges": [
                {"from": "Concept1", "to": "Concept2", "label": "relation description"},
                    ...
                {"from": "ConceptN-1", "to": "ConceptN", "label": "relation description"}]
        }
        Paper content:"""
        "<|eot_id|>"
        "<|start_header_id|>user<|end_header_id|>\n\n"
        f"{data.text}"
        "<|eot_id|>"
        "<|start_header_id|>assistant<|end_header_id|>\n\n"
    )
    response = llm.create_completion(
        prompt=prompt,
        max_tokens=-1,
        temperature=0.2,
    )
    print(response)
    result = response['choices'][0]['text']
    try:
        data = extract_json(result)
    except Exception as e:
        return {"error": "JSON parse failed", "detail": str(e), "raw": data}

    net = Network(height="800px", width="100%", directed=True)
    for node in data["nodes"]:
        net.add_node(node["id"], label=node.get("label", node["id"]))
    for edge in data["edges"]:
        net.add_edge(edge["from"], edge["to"], label=edge.get("label", ""))

    # Pyvis graph를 HTML 문자열로 반환
    html_path = "/tmp/concept_map.html"
    net.save_graph(html_path)
    with open(html_path, "r", encoding="utf-8") as f:
        html_str = f.read()

    return {"html": html_str}

