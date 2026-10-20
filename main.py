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
    st.title("🔢 Mappa Numerologica Completa")
    st.write("Carica la dispensa unica e inserisci i dati anagrafici per elaborare il tema numerologico.")

    api_key = st.secrets.get("OPENAI_API_KEY") or os.environ.get("OPENAI_API_KEY")

    if not api_key:
        st.warning("⚠️ Inserisci la chiave API di OpenAI nei segreti di Streamlit o nelle variabili d'ambiente.")
    else:
        client = OpenAI(api_key=api_key)

    uploaded_pdf = st.file_uploader("Carica la dispensa completa in PDF", type=["pdf"])

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

    user_input = st.text_input("Inserisci Nome, Cognome e Data di Nascita (es. Silvia Cauli 15/08/1973):")

    if st.button("Genera Mappa Completa") and api_key:
        if user_input:
            with st.spinner("Elaborazione della Mappa Numerologica in corso..."):
                try:
                    prompt = f"""
Sei un esperto Maestro Numerologo specializzato nella metodologia della "Scuola Numerica".
Usa la seguente dispensa completa come UNICA FONTE DI RIFERIMENTO per la tabella di conversione (Guematria/Pitagorica), le regole matematiche di calcolo, la riduzione teosofica e le interpretazioni filosofiche/alchemiche:

--- INIZIO DISPENSA DI RIFERIMENTO ---
{pdf_text}
--- FINE DISPENSA DI RIFERIMENTO ---

Dati dell'utente: {user_input}

Genera un prospetto e un'analisi numerologica completa e rigorosa strutturata ESATTAMENTE nei seguenti capitoli:

1. 📐 CALCOLI PASSO PASSO E DERIVAZIONI
   - Mostra la traslitterazione delle lettere in numeri seguendo la tabella pitagorea.
   - Mostra la separazione delle Vocali (Anima) e delle Consonanti (Persona) ed eventualmente le eccezioni della lettera Y.
   - Mostra i conteggi completi di:
     * Numero dell'Anima (A)
     * Numero della Persona (P)
     * Numero dell'Io / Espressione (I)
     * Numero del Destino (D) (somma giorno + mese + anno prima della riduzione)
     * Numero della Quintessenza (Q) (somma Io + Destino prima della riduzione)
     * Approdo (giorno di nascita esatto, non ridotto)
     * Numero del Sole / Forza (giorno + mese) e stima dell'Innesto (età anagrafica di svolta)
     * Numero dell'Origine (O) e Numero del Dono (D) dall'anno di nascita
     * Numeri dell'Ombra: Sotto-sfida Infanzia, Sotto-sfida Maturità e Sfida Principale (mediante sottrazioni)
     * Rilevazione dei Numeri Maestri (11, 22, 33, 44) e Karmici (13, 14, 16, 19) presenti nei calcoli intermedi.

2. ✝️ CROCE CARDINALE NUMEROLOGICA
   - Sintetizza i 5 numeri cardinali (Destino, Io, Persona, Anima, Quintessenza) con le loro derivazioni (es. 28/10/1) e descrivi il loro flusso dinamico dal piano concreto allo spirituale, ponendo la Quintessenza al centro come equilibratore.

3. 📊 GRIGLIA DI AUSTIN COATES & PIANO F.E.M.S.
   - Evidenzia gli Archetipi Dominanti (AD) (numeri più ripetuti) e le Lezioni Karmiche (LK) (numeri assenti).
   - Compila la tabella F.E.M.S. (Fisico, Emotivo, Mentale, Spirituale) contando la frequenza delle lettere/numeri dal nome e cognome e associa la dominanza degli Elementi della Natura (Terra, Acqua, Aria, Fuoco).

4. 🔮 INTERPRETAZIONE Dettagliata & OPERA ALCHEMICA SU DI SÉ
   - Per ciascun numero calcolato e per le relative sfide/punti di forza, fornisci un'interpretazione profonda basata integralmente sui testi della dispensa (Luci, Ombre, Archetipi correlati, trasformazione dal Piombo all'Oro).

Sii estremamente preciso nei passaggi matematici per evitare errori di somma!
"""
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[{"role": "user", "content": prompt}],
                        temperature=0.2
                    )
                    st.subheader("📜 Risultato del Tema Numerologico")
                    st.markdown(response.choices[0].message.content)
                except Exception as e:
                    st.error(f"Si è verificato un errore con OpenAI: {e}")
        else:
            st.warning("Per favore inserisci i dati prima di procedere.")
