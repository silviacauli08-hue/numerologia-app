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

# --- TABELLA PITAGORICA ESATTA (Guematria) ---
TABELLA_PITAGORICA = {
    'a': 1, 'j': 1, 's': 1,
    'b': 2, 'k': 2, 't': 2,
    'c': 3, 'l': 3, 'u': 3,
    'd': 4, 'm': 4, 'v': 4,
    'e': 5, 'n': 5, 'w': 5,
    'f': 6, 'o': 6, 'x': 6,
    'g': 7, 'p': 7, 'y': 7,
    'h': 8, 'q': 8, 'z': 8,
    'i': 9, 'r': 9
}

VOCALI_BASE = set(['a', 'e', 'i', 'o', 'u'])

def riduci(n):
    """Riduzione teosofica fino a singola cifra o numero maestro."""
    while n > 9 and n not in [11, 22, 33, 44]:
        n = sum(int(c) for c in str(n))
    return n

def calcola_nome_cognome(testo):
    testo_clean = testo.lower()
    
    vocali_trovate = []
    consonanti_trovate = []
    
    for char in testo_clean:
        if char in TABELLA_PITAGORICA:
            val = TABELLA_PITAGORICA[char]
            if char in VOCALI_BASE:
                vocali_trovate.append((char.upper(), val))
            elif char == 'y':
                # Regola Y: se non ci sono altre vocali è vocale, altrimenti consonante
                vocali_trovate.append((char.upper(), val))
            else:
                consonanti_trovate.append((char.upper(), val))
                
    tot_v = sum(v[1] for v in vocali_trovate)
    tot_c = sum(c[1] for c in consonanti_trovate)
    tot_io = tot_v + tot_c
    
    return {
        "vocali_dettaglio": vocali_trovate,
        "consonanti_dettaglio": consonanti_trovate,
        "anima_tot": tot_v, "anima_rid": riduci(tot_v),
        "persona_tot": tot_c, "persona_rid": riduci(tot_c),
        "io_tot": tot_io, "io_rid": riduci(tot_io)
    }

def calcola_data_nascita(g, m, a):
    g, m, a = int(g), int(m), int(a)
    
    # Destino: Giorno + Mese + Anno
    dest_tot = g + m + a
    dest_rid = riduci(dest_tot)
    
    # Sole / Forza
    sole_tot = g + m
    sole_rid = riduci(sole_tot)
    
    # Origine (somma cifre anno)
    origine_tot = sum(int(c) for c in str(a))
    origine_rid = riduci(origine_tot)
    
    # Dono (ultime due cifre anno)
    dono_tot = int(str(a)[-2:])
    dono_rid = riduci(dono_tot)
    
    return {
        "dest_tot": dest_tot, "dest_rid": dest_rid,
        "approdo": g,
        "sole_tot": sole_tot, "sole_rid": sole_rid,
        "origine_tot": origine_tot, "origine_rid": origine_rid,
        "dono_tot": dono_tot, "dono_rid": dono_rid
    }

if check_password():
    st.title("🔢 Mappa Numerologica Precisione Matematica")
    st.write("Calcolo nativo Python della Scuola Numerica con interpretazione AI da PDF.")

    api_key = st.secrets.get("OPENAI_API_KEY") or os.environ.get("OPENAI_API_KEY")

    if not api_key:
        st.warning("⚠️ Inserisci la chiave API di OpenAI nei segreti di Streamlit.")
    else:
        client = OpenAI(api_key=api_key)

    uploaded_pdf = st.file_uploader("Carica la dispensa unica in PDF", type=["pdf"])

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

    col1, col2 = st.columns(2)
    with col1:
        nome_cognome = st.text_input("Nome e Cognome:", value="Silvia Cauli")
    with col2:
        data_nascita = st.text_input("Data di Nascita (GG/MM/AAAA):", value="15/08/1973")

    if st.button("Genera Analisi Esatta") and api_key:
        if nome_cognome and data_nascita:
            with st.spinner("Calcolo matematico rigoroso in corso..."):
                try:
                    res_nc = calcola_nome_cognome(nome_cognome)
                    
                    p = data_nascita.split("/")
                    res_d = calcola_data_nascita(p[0], p[1], p[2])
                    
                    # Quintessenza
                    q_tot = res_nc["io_tot"] + res_d["dest_tot"]
                    q_rid = riduci(q_tot)
                    
                    # Stringa con tutti i conteggi lettera per lettera
                    str_vocali = " + ".join([f"{char}({v})" for char, v in res_nc["vocali_dettaglio"]])
                    str_cons = " + ".join([f"{char}({v})" for char, v in res_nc["consonanti_dettaglio"]])
                    
                    report_matematico = f"""
📐 **CALCOLI MATEMATICI ESATTI (Python)**:
- **Nome e Cognome**: {nome_cognome}
- **Data di nascita**: {data_nascita}

1. **Numero dell'Anima (Vocali)**: {str_vocali} = {res_nc['anima_tot']} → **{res_nc['anima_rid']}** ({res_nc['anima_tot']}/{res_nc['anima_rid']})
2. **Numero della Persona (Consonanti)**: {str_cons} = {res_nc['persona_tot']} → **{res_nc['persona_rid']}** ({res_nc['persona_tot']}/{res_nc['persona_rid']})
3. **Numero dell'Io (Espressione)**: {res_nc['anima_tot']} + {res_nc['persona_tot']} = {res_nc['io_tot']} → **{res_nc['io_rid']}** ({res_nc['io_tot']}/{res_nc['io_rid']})
4. **Numero del Destino**: {p[0]} + {p[1]} + {p[2]} = {res_d['dest_tot']} → **{res_d['dest_rid']}** ({res_d['dest_tot']}/{res_d['dest_rid']})
5. **Numero di Approdo (Giorno)**: **{res_d['approdo']}**
6. **Numero del Sole / Forza**: {p[0]} + {p[1]} = {res_d['sole_tot']} → **{res_d['sole_rid']}** (Innesto a {res_d['sole_tot']} anni)
7. **Numero dell'Origine**: {res_d['origine_tot']} → **{res_d['origine_rid']}**
8. **Numero del Dono**: {res_d['dono_tot']} → **{res_d['dono_rid']}**
9. **Numero della Quintessenza**: {res_nc['io_tot']} + {res_d['dest_tot']} = {q_tot} → **{q_rid}**
"""

                    st.markdown("### 📊 Risultato dei Calcoli Matematici")
                    st.info(report_matematico)

                    # Invio all'IA per l'interpretazione basata sul PDF
                    prompt = f"""
Sei un esperto Maestro Numerologo della Scuola Numerica.
Usa ESCLUSIVAMENTE la seguente dispensa per interpretare i significati, gli archetipi, le luci e le ombre dei numeri.

UTILIZZA QUESTI NUMERI ESATTI CALCOLATI DAL SISTEMA:
{report_matematico}

DISPENSA PDF:
{pdf_text}

ISTRUZIONI PER L'INTERPRETAZIONE:
1. Riporta in cima la sezione dei calcoli sopra fornita.
2. Descrivi la **Croce Cardinale Numerologica** (Destino, Io, Persona, Anima, Quintessenza).
3. Fornisci l'**Interpretazione Dettagliata dell'Opera Alchemica** per ciascun numero emerso usando i testi della dispensa.
"""

                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[{"role": "user", "content": prompt}],
                        temperature=0.2
                    )

                    st.subheader("🔮 Interpretazione Numerologica Dettagliata")
                    st.markdown(response.choices[0].message.content)

                except Exception as e:
                    st.error(f"Si è verificato un errore: {e}")
        else:
            st.warning("Compila tutti i campi.")
