import streamlit as st
import requests
import json
import PyPDF2

def extract_text_from_files(uploaded_files):
    all_text = ""
    for file in uploaded_files:
        if file.name.endswith('.txt'):
            all_text += file.read().decode() + "\n\n"
        elif file.name.endswith('.pdf'):
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                all_text += page.extract_text() + "\n\n"
    return all_text

def ask_ollama_with_context(question, context, model="llama2"):
    prompt = f"""You are an AI assistant. Use the following context to answer the question.
    
Context:
{context}

Question: {question}

Answer based on the context:"""
    
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0}
            },
            timeout=60
        )
        
        if response.status_code == 200:
            return response.json()["response"]
        else:
            return f"Error: Could not get response from Ollama. Status: {response.status_code}"
    
    except requests.exceptions.ConnectionError:
        return "Error: Cannot connect to Ollama. Make sure 'ollama serve' is running."
    except Exception as e:
        return f"Error: {str(e)}"

def check_ollama_models():
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            return [model["name"] for model in response.json().get("models", [])]
        return []
    except:
        return []

st.set_page_config(page_title="Q1: Open-Source LLM", layout="wide")
st.title("Question 1: Open-Source LLM App")

available_models = check_ollama_models()
if not available_models:
    st.error("Ollama is not running or no models available. Please run 'ollama serve' and pull a model first.")
    st.info("Run these commands in terminal:\n1. ollama serve\n2. ollama pull llama2")
    st.stop()

selected_model = st.sidebar.selectbox("Select Model", available_models)

uploaded_files = st.sidebar.file_uploader(
    "Upload Documents (PDF/TXT)",
    type=["pdf", "txt"],
    accept_multiple_files=True
)

context_text = ""
if uploaded_files:
    with st.spinner("Reading documents..."):
        context_text = extract_text_from_files(uploaded_files)
        if context_text.strip():
            st.success(f"Loaded {len(uploaded_files)} document(s)")
            st.session_state.context = context_text
        else:
            st.warning("No text could be extracted from documents")

if "context" in st.session_state:
    question = st.text_input("Ask a question about your documents:")
    
    if question:
        with st.spinner("Getting answer from Ollama..."):
            answer = ask_ollama_with_context(
                question, 
                st.session_state.context[:4000], 
                selected_model
            )
            
            st.subheader("Answer:")
            st.write(answer)
            
            with st.expander("View Context Used"):
                st.text(st.session_state.context[:1000] + "...")
else:
    st.info("Upload documents to ask questions about them")