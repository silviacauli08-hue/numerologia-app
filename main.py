import os
import streamlit as st
from openai import OpenAI
from pypdf import PdfReader

# Configurazione della pagina Streamlit
st.set_page_config(page_title="App di Numerologia", layout="centered")

st.title("🔢 Applicazione di Numerologia con OpenAI")
st.write("Carica le dispense in PDF e inserisci i dati per generare il profilo numerologico.")

# Inizializzazione del client OpenAI (legge la chiave dalle variabili d'ambiente o dai secrets)
api_key = st.secrets.get("OPENAI_API_KEY") or os.environ.get("OPENAI_API_KEY")

if not api_key:
st.warning("⚠️ Inserisci la chiave API di OpenAI nei segreti di Streamlit o nelle variabili d'ambiente.")
else:
client = OpenAI(api_key=api_key)

# Sezione per il caricamento dei file PDF delle dispense
uploaded_pdf = st.file_uploader("Carica una dispensa in PDF", type=["pdf"])

pdf_text = ""
if uploaded_pdf is not None:
try:
reader = PdfReader(uploaded_pdf)
for page in reader.pages:
text = page.extract_text()
if text:
pdf_text += text + "\n"
st.success(f"PDF caricato con successo! Estratte {len(reader.pages)} pagine.")
except Exception as e:
st.error(f"Errore durante la lettura del PDF: {e}")

# Input utente per la numerologia
user_input = st.text_input("Inserisci nome, cognome e data di nascita:")

if st.button("Genera Profilo Numerologico"):
if not api_key:
st.error("Configura la chiave API di OpenAI per procedere.")
elif not user_input:
st.warning("Inserisci i dati richiesti prima di generare il profilo.")
else:
with st.spinner("Elaborazione in corso..."):
prompt = f"""
Agisci come un esperto numerologo. Utilizzando le informazioni estratte dalla dispensa (se presenti)
e i dati forniti dall'utente ({user_input}), elabora un profilo numerologico dettagliato.

Contenuto della dispensa di riferimento:
{pdf_text[:3000]}
"""

try:
response = client.chat.completions.create(
model="gpt-3.5-turbo",
messages=[
{"role": "system", "content": "Sei un assistente esperto in numerologia."},
{"role": "user", "content": prompt}
]
)
result = response.choices[0].message.content
st.subheader("Risultato del Profilo Numerologico:")
st.write(result)
except Exception as e:
st.error(f"Errore nella comunicazione con OpenAI: {e}")
