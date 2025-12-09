import streamlit as st
import requests
import PyPDF2
import os

def read_pdf(file):
    pdf_reader = PyPDF2.PdfReader(file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() + "\n"
    return text

def read_txt(file):
    return file.read().decode()

def ask_groq(api_key, question, context=""):
    url = "https://api.groq.com/openai/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    prompt = f"Context: {context}\n\nQuestion: {question}\n\nAnswer:"
    
    data = {
        "model": "llama-3.1-8b-instant",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            return f"API Error: {response.status_code}"
    
    except Exception as e:
        return f"Error: {str(e)}"

st.set_page_config(page_title="Q4: Closed-Source LLM", layout="wide")
st.title("Question 4: Closed-Source LLM App")

st.sidebar.header("API Configuration")
api_key = st.sidebar.text_input("Groq API Key", type="password")

if not api_key:
    api_key = os.environ.get("GROQ_API_KEY")

if not api_key:
    st.error("Please enter Groq API key")
    st.info("Get free key from: https://console.groq.com")
    st.stop()

uploaded_files = st.sidebar.file_uploader(
    "Upload Documents (PDF/TXT)",
    type=["pdf", "txt"],
    accept_multiple_files=True
)

context = ""
if uploaded_files:
    context = ""
    for file in uploaded_files:
        if file.name.endswith('.pdf'):
            context += read_pdf(file) + "\n\n"
        elif file.name.endswith('.txt'):
            context += read_txt(file) + "\n\n"
    
    st.success(f"Loaded {len(uploaded_files)} document(s)")
    st.session_state.context = context

question = st.text_input("Ask a question about your documents:")

if st.button("Get Answer") and question:
    if "context" in st.session_state:
        context_to_use = st.session_state.context[:4000]
    else:
        context_to_use = ""
    
    with st.spinner("Querying Groq API..."):
        answer = ask_groq(api_key, question, context_to_use)
        
        st.subheader("Answer:")
        st.write(answer)
        
        st.caption(f"Using Groq API with llama-3.1-8b-instant model")