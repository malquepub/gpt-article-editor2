import streamlit as st
import openai
import docx
from docx import Document
import tempfile
import shutil
import difflib
from datetime import datetime

# -------------------
# CONFIGURAÇÃO OPENAI
# -------------------
API_KEY = "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"
openai.api_key = API_KEY

# -------------------
# FUNÇÃO PARA REVISAR TEXTO COM O GPT
# -------------------
def review_text_with_gpt(text):
    prompt = (
        "You are an expert in academic writing. Improve the following text for grammar, clarity, and academic style without changing its meaning. "
        "Do not add comments or explanations—just return the improved text.\n\n"
        f"{text}"
    )
    
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are an expert academic editor."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.1,
        max_tokens=1500,
    )

    return response.choices[0].message['content'].strip()

# -------------------
# FUNÇÃO PARA ADICIONAR ALTERAÇÕES (TRACK CHANGES)
# -------------------
def apply_track_changes(original_text, revised_text):
    diff = list(difflib.ndiff(original_text.split(), revised_text.split()))
    tracked_text = ""

    for word in diff:
        if word.startswith('- '):
            tracked_text += f"[DELETED: {word[2:]}] "
        elif word.startswith('+ '):
            tracked_text += f"[ADDED: {word[2:]}] "
        elif word.startswith('  '):
            tracked_text += f"{word[2:]} "

    return tracked_text.strip()

# -------------------
# FUNÇÃO PARA PROCESSAR O DOCUMENTO WORD
# -------------------
def process_word_document(uploaded_file):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as temp_input:
        shutil.copyfileobj(uploaded_file, temp_input)

    doc = Document(temp_input.name)
    
    for para in doc.paragraphs:
        original_text = para.text.strip()
        if original_text:
            revised_text = review_text_with_gpt(original_text)
            tracked_text = apply_track_changes(original_text, revised_text)

            # Substitui o texto original pelo texto com alterações
            para.text = tracked_text

    # Salva o documento revisado
    output_path = tempfile.NamedTemporaryFile(delete=False, suffix="_tracked.docx").name
    doc.save(output_path)

    return output_path

# -------------------
# INTERFACE STREAMLIT
# -------------------
st.title("📄 MalquePub Editing Services - Track Changes")

st.write("""
Upload a Word document (.docx) and receive a version with grammar and academic style improvements. 
Corrections will be provided with tracked changes (additions and deletions highlighted). 
""")

uploaded_file = st.file_uploader("Upload your Word document:", type=["docx"])

if uploaded_file and st.button("🚀 Process Document"):
    with st.spinner("Processing... Please wait."):
        output_path = process_word_document(uploaded_file)
        
        st.success("✅ Document processed successfully!")
        
        with open(output_path, "rb") as file:
            st.download_button(
                label="⬇️ Download Revised Document",
                data=file,
                file_name=f"revised_with_track_changes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
