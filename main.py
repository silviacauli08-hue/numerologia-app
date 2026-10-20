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
    while n > 9 and n not in [11, 22, 33, 44]:
        n = sum(int(c) for c in str(n))
    return n

def riduci_singola(n):
    while n > 9:
        n = sum(int(c) for c in str(n))
    return n

def calcola_nome_cognome(testo):
    testo_clean = testo.lower()
    vocali_trovate = []
    consonanti_trovate = []
    
    for char in testo_clean:
        if char in TABELLA_PITAGORICA:
            val = TABELLA_PITAGORICA[char]
            if char in VOCALI_BASE or char == 'y':
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
    dest_tot = g + m + a
    dest_rid = riduci(dest_tot)
    sole_tot = g + m
    sole_rid = riduci(sole_tot)
    origine_tot = sum(int(c) for c in str(a))
    origine_rid = riduci(origine_tot)
    dono_tot = int(str(a)[-2:])
    dono_rid = riduci(dono_tot)
    
    m_s = riduci_singola(m)
    g_s = riduci_singola(g)
    a_s = riduci_singola(sum(int(c) for c in str(a)))
    
    sfida_infanzia = abs(g_s - a_s)
    sfida_maturita = abs(m_s - g_s)
    sfida_principale = abs(sfida_maturita - sfida_infanzia)
    
    return {
        "dest_tot": dest_tot, "dest_rid": dest_rid,
        "approdo": g,
        "sole_tot": sole_tot, "sole_rid": sole_rid,
        "origine_rid": origine_rid,
        "dono_rid": dono_rid,
        "sfida_infanzia": sfida_infanzia,
        "sfida_maturita": sfida_maturita,
        "sfida_principale": sfida_principale
    }

if check_password():
    st.title("🔢 Mappa Numerologica Armoniosa")
    st.write("Genera il profilo numerologico completo, fluido e in italiano perfetto.")

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

    if st.button("Genera Analisi Corretta e Armoniosa") and api_key:
        if nome_cognome and data_nascita:
            with st.spinner("Generazione dell'analisi in lingua italiana impeccabile..."):
                try:
                    res_nc = calcola_nome_cognome(nome_cognome)
                    p = data_nascita.split("/")
                    res_d = calcola_data_nascita(p[0], p[1], p[2])
                    
                    q_tot = res_nc["io_tot"] + res_d["dest_tot"]
                    q_rid = riduci(q_tot)
                    
                    report_matematico = f"""
DATI MATEMATICI ESATTI DI RIFERIMENTO:
- Persona analizzata: {nome_cognome} (data di nascita: {data_nascita})
- Numero dell'Anima: {res_nc['anima_tot']}/{res_nc['anima_rid']}[cite: 3]
- Numero della Persona: {res_nc['persona_tot']}/{res_nc['persona_rid']}[cite: 3]
- Numero dell'Io (Espressione): {res_nc['io_tot']}/{res_nc['io_rid']}[cite: 3]
- Numero del Destino: {res_d['dest_tot']}/{res_d['dest_rid']}[cite: 3]
- Approdo (Giorno esatto): {res_d['approdo']}[cite: 3]
- Sole / Forza: {res_d['sole_tot']}/{res_d['sole_rid']} (Età dell'Innesto: {res_d['sole_tot']} anni)[cite: 3]
- Origine: {res_d['origine_rid']} | Dono: {res_d['dono_rid']}[cite: 3]
- Quintessenza: {q_tot}/{q_rid}[cite: 3]
- Sotto-sfida Infanzia/Giovinezza: {res_d['sfida_infanzia']}[cite: 3]
- Sotto-sfida Maturità: {res_d['sfida_maturita']}[cite: 3]
- Sfida Principale (Ombra): {res_d['sfida_principale']}[cite: 3]
"""

                    prompt = f"""
Sei un Maestro Numerologo raffinato, profondo e saggio della Scuola Numerica.
Scrivi un'interpretazione in LINGUA ITALIANA CORRETTA, FLUIDA, SINTATTICAMENTE IMPECCABILE E ARMONIOSA.

RICOSTRUISCI IL PROFILO USANDO ESCLUSIVAMENTE QUESTI NUMERI ESATTI:
{report_matematico}

DISPENSA DI RIFERIMENTO (Scuola Numerica):
{pdf_text}

REGOLE DI SCRITTURA RIGIDE:
1. Scrivi esclusivamente in lingua italiana con sintassi perfetta, fluida e senza ripetizioni di parole o frasi sconnesse.
2. Evita elenchi puntati o tabelle fredde. Usa un linguaggio caldo, poetico, narrativo, alchemico ed empatico.
3. Articola il testo nei seguenti capitoli discorsivi:
   - 🌅 **L'Ingresso nel Viaggio e l'Approdo**: Introduci la persona ({nome_cognome}), la data di nascita e il valore del giorno di approdo ({res_d['approdo']}).
   - 🎶 **La Sinfonia del Nome: Anima, Persona e Io**: Spiega come dialogano l'Anima ({res_nc['anima_tot']}/{res_nc['anima_rid']}), la Persona ({res_nc['persona_tot']}/{res_nc['persona_rid']}) e l'Io ({res_nc['io_tot']}/{res_nc['io_rid']}).
   - 🌱 **Il Cammino dei Talenti**: Descrivi il Destino ({res_d['dest_tot']}/{res_d['dest_rid']}), il Sole/Forza ({res_d['sole_tot']}/{res_d['sole_rid']} con l'Innesto a {res_d['sole_tot']} anni), l'Origine e il Dono.
   - 🌑 **Il Cammino delle Sfide e dell'Ombra**: Spiega la Sotto-sfida d'infanzia ({res_d['sfida_infanzia']}), di maturità ({res_d['sfida_maturita']}) e la Sfida Principale ({res_d['sfida_principale']}) in chiave evolutiva ("il seme del proprio superamento").
   - 🔮 **La Quintessenza e la Croce Cardinale**: Concludi con la Quintessenza ({q_tot}/{q_rid}) e la sintesi della Croce Cardinale come centro di equilibrio e missione dell'anima.
"""

                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[{"role": "user", "content": prompt}],
                        temperature=0.2 # Bassa per evitare allucinazioni o frasi sconnesse
                    )

                    st.subheader("📖 Profilo Numerologico Completo e Impeccabile")
                    st.markdown(response.choices[0].message.content)

                except Exception as e:
                    st.error(f"Si è verificato un errore: {e}")
        else:
            st.warning("Compila tutti i campi.")
