import streamlit as st
import requests
import streamlit.components.v1 as components

st.set_page_config(page_title="논문 개념 관계도", layout="centered")
st.title("📚 논문 개념 관계도 생성기")

paper_text = st.text_area("논문 전문 또는 요약을 입력하세요", height=300)

if st.button("Submit"):
    if not paper_text.strip():
        st.warning("Please write some text.")
    else:
        with st.spinner("Analyzing the paper..."):
            response = requests.post("http://localhost:8000/api/generate_graph", json={"text": paper_text})
            if response.status_code == 200:
                data = response.json()
                print(data)
                if "html" in data:
                    components.html(data["html"], height=650)
                else:
                    st.error("server error: " + str(data))
            else:
                st.error(f"HTTP error {response.status_code}: {response.text}")