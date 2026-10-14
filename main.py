import os
import streamlit as st
from openai import OpenAI
from pypdf import PdfReader

st.set_page_config(page_title="App di Numerologia", layout="centered")

st.title("🔢 Applicazione di Numerologia con OpenAI")
st.write("Carica le dispense in PDF e inserisci i dati per generare l'analisi.")

api_key = st.secrets.get("OPENAI_API_KEY") or os.environ.get("OPENAI_API_KEY")

if not api_key:
    st.warning("⚠️ Inserisci la chiave API di OpenAI nei segreti di Streamlit o nelle variabili d'ambiente.")
else:
    client = OpenAI(api_key=api_key)

uploaded_pdf = st.file_uploader("Carica una dispensa in PDF", type=["pdf"])

pdf_text = ""
if uploaded_pdf is not None:
    try:
        reader = PdfReader(uploaded_pdf)
        for page in reader.pages:
            text = page.extract_text()
            if text:
                pdf_text += text + "\n"
        st.success("PDF caricato ed estratto con successo!")
    except Exception as e:
        st.error(f"Errore nella lettura del PDF: {e}")

user_input = st.text_input("Inserisci nome, cognome e data di nascita:")

if st.button("Genera Analisi") and api_key:
    if user_input:
        with st.spinner("Generazione in corso..."):
            try:
                prompt = f"Agisci come un esperto numerologo. Usa queste informazioni di riferimento dalle dispense:\n{pdf_text}\n\nGenera un'analisi numerologica per: {user_input}"
                response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}]
                )
                st.subheader("Risultato dell'Analisi")
                st.write(response.choices[0].message.content)
            except Exception as e:
                st.error(f"Si è verificato un errore con OpenAI: {e}")
else:
    st.warning("Per favore inserisci i dati prima di procedere.")
