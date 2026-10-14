import os
import streamlit as st
from openai import OpenAI
from pypdf import PdfReader

st.set_page_config(page_title="App di Numerologia", layout="centered")

def check_password():
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False
    if st.session_state["password_correct"]:
        return True

    st.title("🔒 Accesso Riservato")
    password_input = st.text_input("Inserisci la password per accedere all'app:", type="password")
    
    if st.button("Accedi"):
        if password_input == "numerologia2026":
            st.session_state["password_correct"] = True
            st.rerun()
        else:
            st.error("❌ Password errata!")
    return False

if check_password():
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
                    prompt = f"""
Sei un esperto numerologo e matematico rigoroso.

USA LE SEGUENTI DISPENSE COME UNICA FONTE DI RIFERIMENTO E REGOLE DI CALCOLO:
{pdf_text}

ISTRUZIONI PER L'ANALISI:
1. Identifica chiaramente nome, cognome e data di nascita dai dati forniti dall'utente: {user_input}.
2. Esegui i calcoli numerologici segnale nelle dispense applicando scrupolosamente le somme e le conversioni specificate.
3. MOSTRA SEMPRE IL CALCOLO PASSO PASSO (es. somma delle singole cifre della data di nascita, riduzione a cifra singola o numero maestro).
4. Fornisci l'interpretazione completa e dettagliata per ciascun numero calcolato, basandoti unicamente sul testo delle dispense caricate.

Inizia fornendo prima la sezione "📐 CALCOLI PASSO PASSO" e poi la sezione "🔮 INTERPRETAZIONE NUMEROLOGICA".
"""
                    response = client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[{"role": "user", "content": prompt}],
                        temperature=0.2  # Bassa creatività per garantire massima accuratezza nei calcoli
                    )
                    st.subheader("Risultato dell'Analisi")
                    st.write(response.choices[0].message.content)
                except Exception as e:
                    st.error(f"Si è verificato un errore con OpenAI: {e}")
        else:
            st.warning("Per favore inserisci i dati prima di procedere.")
