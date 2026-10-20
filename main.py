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

# --- FUNZIONI DI CALCOLO MATEMATICO ESATTO ---
def riduci_teosofico(n):
    """Riduce un numero a una cifra singola, preservando i numeri maestri se desiderato."""
    while n > 9 and n not in [11, 22, 33, 44]:
        n = sum(int(c) for c in str(n))
    return n

def calcola_guematria(testo):
    """Calcola Anima (vocali), Persona (consonanti) e Io (totale) secondo la tabella pitagorica."""
    tabella = {
        'a': 1, 'b': 2, 'c': 3, 'd': 4, 'e': 5, 'f': 6, 'g': 7, 'h': 8, 'i': 9,
        'j': 1, 'k': 2, 'l': 3, 'm': 4, 'n': 5, 'o': 6, 'p': 7, 'q': 8, 'r': 9,
        's': 1, 't': 2, 'u': 3, 'v': 4, 'w': 5, 'x': 6, 'y': 7, 'z': 8
    }
    vocali = set(['a', 'e', 'i', 'o', 'u', 'y'])
    
    testo = testo.lower()
    tot_vocali = 0
    tot_consonanti = 0
    
    for char in testo:
        if char in tabella:
            valore = tabella[char]
            if char in vocali:
                tot_vocali += valore
            else:
                tot_consonanti += valore
                
    tot_io = tot_vocali + tot_consonanti
    
    return {
        "anima_tot": tot_vocali, "anima_rid": riduci_teosofico(tot_vocali),
        "persona_tot": tot_consonanti, "persona_rid": riduci_teosofico(tot_consonanti),
        "io_tot": tot_io, "io_rid": riduci_teosofico(tot_io)
    }

def calcola_data(giorno, mese, anno):
    """Calcola Destino, Approdo, Sole, Origine, Dono e Sfide dalla data di nascita."""
    g, m, a = int(giorno), int(mese), int(anno)
    
    # Destino: somma intera data
    dest_tot = g + m + a
    dest_rid = riduci_teosofico(dest_tot)
    
    # Approdo (giorno esatto)
    approdo = g
    
    # Sole / Forza
    sole_tot = g + m
    sole_rid = riduci_teosofico(sole_tot)
    
    # Origine e Dono dall'anno
    anno_str = str(a)
    origine_tot = sum(int(c) for c in anno_str)
    origine_rid = riduci_teosofico(origine_tot)
    
    dono_tot = int(anno_str[-2:])
    dono_rid = riduci_teosofico(dono_tot)
    
    # Quintessenza (Io totale + Destino totale prima della riduzione finale)
    return {
        "dest_tot": dest_tot, "dest_rid": dest_rid,
        "approdo": approdo,
        "sole_tot": sole_tot, "sole_rid": sole_rid,
        "origine_rid": origine_rid,
        "dono_rid": dono_rid
    }


if check_password():
    st.title("🔢 Mappa Numerologica con Calcoli Esatti")
    st.write("Carica la dispensa unica e inserisci i dati per generare l'analisi con calcoli matematici garantiti.")

    api_key = st.secrets.get("OPENAI_API_KEY") or os.environ.get("OPENAI_API_KEY")

    if not api_key:
        st.warning("⚠️ Inserisci la chiave API di OpenAI nei segreti di Streamlit.")
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

    # Campi separati per inserire nome, cognome e data per evitare errori di input
    col1, col2 = st.columns(2)
    with col1:
        nome_cognome = st.text_input("Nome e Cognome:", value="Silvia Cauli")
    with col2:
        data_nascita = st.text_input("Data di nascita (GG/MM/AAAA):", value="15/08/1973")

    if st.button("Genera Mappa Numerologica") and api_key:
        if nome_cognome and data_nascita:
            with st.spinner("Calcoli matematici e generazione in corso..."):
                try:
                    # 1. Eseguiamo i calcoli matematici esatti in Python
                    res_guematria = calcola_guematria(nome_cognome)
                    
                    parti_data = data_nascita.split("/")
                    g, m, a = parti_data[0], parti_data[1], parti_data[2]
                    res_data = calcola_data(g, m, a)
                    
                    quintessenza_tot = res_guematria["io_tot"] + res_data["dest_tot"]
                    quintessenza_rid = riduci_teosofico(quintessenza_tot)

                    # 2. Creiamo un blocco con i risultati matematici blindati da passare all'IA
                    dati_matematici = f"""
VALORI MATEMATICI CALCOLATI ESATTAMENTE DAL SISTEMA:
- Nome e Cognome analizzati: {nome_cognome}
- Data di Nascita: {data_nascita}
- Numero dell'Anima: {res_guematria['anima_tot']} -> Ridotto: {res_guematria['anima_rid']}
- Numero della Persona: {res_guematria['persona_tot']} -> Ridotto: {res_guematria['persona_rid']}
- Numero dell'Io (Espressione): {res_guematria['io_tot']} -> Ridotto: {res_guematria['io_rid']}
- Numero del Destino (Cammino di Vita): {res_data['dest_tot']} -> Ridotto: {res_data['dest_rid']}
- Numero di Approdo (Giorno): {res_data['approdo']}
- Numero del Sole / Forza: {res_data['sole_tot']} -> Ridotto: {res_data['sole_rid']}
- Numero dell'Origine: {res_data['origine_rid']}
- Numero del Dono: {res_data['dono_rid']}
- Numero della Quintessenza: {quintessenza_tot} -> Ridotto: {quintessenza_rid}
"""

                    # 3. Prompt strutturato per l'IA (usa i dati esatti e interpreta usando il PDF)
                    prompt = f"""
Sei un esperto Maestro Numerologo della "Scuola Numerica". 
Usa la dispensa allegata come unica fonte per l'interpretazione dei significati, degli archetipi, delle luci e delle ombre.

{dati_matematici}

DISPENSA DI RIFERIMENTO:
{pdf_text}

ISTRUZIONI PER L'OUTPUT:
Presenta l'analisi strutturata in questo modo:
1. 📐 **I CALCOLI DELLA MAPPA** (Riporta esattamente i numeri calcolati dal sistema sopra elencati, mostrando i passaggi chiave).
2. ✝️ **LA CROCE CARDINALE NUMEROLOGICA** (Descrivi il significato dei 5 numeri fondamentali: Anima, Persona, Io, Destino, Quintessenza).
3. 🔮 **INTERPRETAZIONE PROFONDA E OPERA ALCHEMICA** (Fornisci l'interpretazione dettagliata di ciascuno di questi numeri pescando i testi, le definizioni di luce/ombra e gli archetipi direttamente dalla dispensa).
"""

                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[{"role": "user", "content": prompt}],
                        temperature=0.2
                    )
                    
                    st.subheader("📜 Risultato della Mappa Numerologica")
                    st.markdown(response.choices[0].message.content)
                    
                except Exception as e:
                    st.error(f"Si è verificato un errore: {e}")
        else:
            st.warning("Per favore compila tutti i campi.")
