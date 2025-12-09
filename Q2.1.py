import streamlit as st
import re
import PyPDF2

def extract_text_from_pdf(file):
    pdf_reader = PyPDF2.PdfReader(file)
    text = ""
    for page in pdf_reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text

def find_all_abbreviations(text):
    abbreviations = {}
    
    patterns = [
        r'([A-Z][A-Za-z\s\-]{2,})\s*\(([A-Z]{2,})\)',
        r'([A-Z]{2,})\s*\(([A-Z][A-Za-z\s\-]{2,})\)',
        r'\b([A-Z]{2,})\b\s*[=\-\:]\s*([A-Z][A-Za-z\s\-]{2,})',
        r'([A-Z][A-Za-z\s\-]{2,})\s*[=\-\:]\s*\b([A-Z]{2,})\b'
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text)
        for match in matches:
            if len(match) == 2:
                term1, term2 = match
                
                if term2.isupper() and 2 <= len(term2) <= 6:
                    abbreviation = term2.strip()
                    full_term = " ".join(term1.strip().split())
                elif term1.isupper() and 2 <= len(term1) <= 6:
                    abbreviation = term1.strip()
                    full_term = " ".join(term2.strip().split())
                else:
                    continue
                
                if abbreviation not in abbreviations:
                    abbreviations[abbreviation] = full_term
    
    return abbreviations

def format_abbreviation_index(abbreviations):
    if not abbreviations:
        return "No abbreviations found."
    
    lines = []
    for abbrev in sorted(abbreviations.keys()):
        lines.append(f"• {abbrev}: {abbreviations[abbrev]}")
    
    return "\n".join(lines)

st.set_page_config(page_title="Q2: Abbreviation Index", layout="wide")
st.title("Question 2: Abbreviation Index Generator")

st.markdown("**Upload the three articles:** Article1.pdf, Article2.pdf, Article3.pdf")

uploaded_files = st.file_uploader(
    "Upload PDF Articles",
    type=["pdf"],
    accept_multiple_files=True
)

if uploaded_files and st.button("Generate Abbreviation Index"):
    for file_idx, uploaded_file in enumerate(uploaded_files):
        st.markdown(f"---")
        st.subheader(f"Article {file_idx + 1}: {uploaded_file.name}")
        
        with st.spinner(f"Processing {uploaded_file.name}..."):
            text = extract_text_from_pdf(uploaded_file)
            
            if not text.strip():
                st.warning(f"No text extracted from {uploaded_file.name}")
                continue
            
            abbreviations = find_all_abbreviations(text)
            
            if abbreviations:
                index_text = format_abbreviation_index(abbreviations)
                
                st.success(f"Found {len(abbreviations)} abbreviations")
                
                st.text_area(
                    f"Abbreviation Index for {uploaded_file.name}",
                    index_text,
                    height=min(300, len(abbreviations) * 25 + 50)
                )
                
                with st.expander("Show found abbreviation patterns"):
                    for line in index_text.split("\n"):
                        st.write(line)
            
            else:
                st.warning("No abbreviations found in standard format")
                
                with st.expander("Show extracted text (first 1000 chars)"):
                    st.text(text[:1000] + "..." if len(text) > 1000 else text)