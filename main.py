import os
import streamlit as st
from openai import OpenAI
from pypdf import PdfReader

# Configurazione pagina
st.set_page_config(page_title="App di Numerologia", layout="centered")

# Impedisce traduzioni automatiche alterate dal browser
st.markdown("""
    <html lang="it" class="notranslate">
    <head><meta name="google" content="notranslate" /></head>
    <style>
        .element-container, .stMarkdown, p, h1, h2, h3 {
            font-family: 'Georgia', serif;
        }
    </style>
""", unsafe_allow_html=True)

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
    st.title("✨ Mappa Numerologica Evolutiva")
    st.write("Analisi narrativa profonda e pratica basata sulla Scuola Numerica.")

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

    if st.button("Genera Analisi Approfondita") and api_key:
        if nome_cognome and data_nascita:
            with st.spinner("Elaborazione del profilo in corso..."):
                try:
                    res_nc = calcola_nome_cognome(nome_cognome)
                    p = data_nascita.split("/")
                    res_d = calcola_data_nascita(p[0], p[1], p[2])
                    
                    q_tot = res_nc["io_tot"] + res_d["dest_tot"]
                    q_rid = riduci(q_tot)
                    
                    # 1. MOSTRA QUADRO SINTETICO DEI RISULTATI
                    st.markdown("---")
                    st.subheader("📊 Mappa dei Numeri Fondamentali")
                    c1, c2, c3, c4, c5 = st.columns(5)
                    c1.metric("Anima (A)", f"{res_nc['anima_tot']}/{res_nc['anima_rid']}")
                    c2.metric("Persona (P)", f"{res_nc['persona_tot']}/{res_nc['persona_rid']}")
                    c3.metric("Io (I)", f"{res_nc['io_tot']}/{res_nc['io_rid']}")
                    c4.metric("Destino (D)", f"{res_d['dest_tot']}/{res_d['dest_rid']}")
                    c5.metric("Quintessenza (Q)", f"{q_tot}/{q_rid}")
                    
                    st.write(f"**Approdo (Giorno)**: {res_d['approdo']} | **Sole/Forza**: {res_d['sole_tot']}/{res_d['sole_rid']} (Innesto: {res_d['sole_tot']} anni) | **Origine**: {res_d['origine_rid']} | **Dono**: {res_d['dono_rid']}")
                    st.write(f"**Sfide**: Infanzia {res_d['sfida_infanzia']} | Maturità {res_d['sfida_maturita']} | **Principale**: {res_d['sfida_principale']}")
                    st.markdown("---")

                    report_matematico = f"""
DATI NUMERICI ESATTI:
- Soggetto: {nome_cognome} ({data_nascita})
- Anima: {res_nc['anima_tot']}/{res_nc['anima_rid']}[cite: 3]
- Persona: {res_nc['persona_tot']}/{res_nc['persona_rid']}[cite: 3]
- Io / Espressione: {res_nc['io_tot']}/{res_nc['io_rid']}[cite: 3]
- Destino / Cammino: {res_d['dest_tot']}/{res_d['dest_rid']}[cite: 3]
- Approdo: {res_d['approdo']}[cite: 3]
- Sole / Forza: {res_d['sole_tot']}/{res_d['sole_rid']} (Innesto: {res_d['sole_tot']} anni)[cite: 3]
- Origine: {res_d['origine_rid']} | Dono: {res_d['dono_rid']}[cite: 3]
- Sotto-sfida Infanzia: {res_d['sfida_infanzia']}[cite: 3]
- Sotto-sfida Maturità: {res_d['sfida_maturita']}[cite: 3]
- Sfida Principale: {res_d['sfida_principale']}[cite: 3]
- Quintessenza: {q_tot}/{q_rid}[cite: 3]
"""

                    prompt = f"""
Sei un Maestro Numerologo raffinato, colto e profondamente empatico della Scuola Numerica.
Scrivi un'analisi narrativa fluida, armoniosa, dettagliata e orientata anche alle applicazioni pratiche e professionali in LINGUA ITALIANA IMPECCABILE.

USO DEI DATI:
{report_matematico}

DISPENSA DI RIFERIMENTO:
{pdf_text}

ISTRUZIONI DI CONTENUTO E STILE:
1. Scrivi esclusivamente in italiano perfetto, elegante e scorrevole. Non ripetere mai parole o sillabe in modo anomalo.
2. Evita elenchi puntati o tabelle fredde. Sviluppa testi organici discorsivi.
3. **Importante**: Quando tratti l'Io (i mezzi d'azione) e il Destino (il cammino di vita), approfondisci concretamente **che cosa la persona è portata a fare nella vita pratica e professionale** in base a quei numeri (es. se c'è il 4, attitudini per metodo, organizzazione, contabilità o tecnica; se c'è l'8, leadership, gestione o impresa; se c'è il 2, mediazione e lavoro con le persone; se c'è l'1, pionierismo o autonomia; ecc., attingendo dai significati della dispensa)[cite: 3].

STRUTTURA CAPITOLI:
- 🌅 **L'Ingresso nel Viaggio e l'Approdo**: Introduzione sull'incarnazione ({nome_cognome}), data ({data_nascita}) e significato del giorno di Approdo ({res_d['approdo']})[cite: 3].
- 🎶 **La Sinfonia del Nome: Anima, Persona e Io**: L'Anelito dell'Anima ({res_nc['anima_tot']}/{res_nc['anima_rid']}), lo Scudo della Persona ({res_nc['persona_tot']}/{res_nc['persona_rid']}) e i mezzi d'azione concreti e professionali dell'Io ({res_nc['io_tot']}/{res_nc['io_rid']})[cite: 3].
- 🌱 **Il Cammino dei Talenti**: Il Destino ({res_d['dest_tot']}/{res_d['dest_rid']}) con le sue inclinazioni di percorso e sbocchi pratici, la Forza del Sole ({res_d['sole_tot']}/{res_d['sole_rid']}) con la svolta dell'Innesto a {res_d['sole_tot']} anni, l'Origine e il Dono[cite: 3].
- 🌑 **Il Cammino delle Sfide e dell'Ombra**: Trasmutazione della Sotto-sfida d'infanzia ({res_d['sfida_infanzia']}), di maturità ({res_d['sfida_maturita']}) e della Sfida Principale ({res_d['sfida_principale']}) viste come "seme del proprio superamento"[cite: 3].
- 🔮 **La Quintessenza e la Croce Cardinale**: Sintesi del centro d'equilibrio ({q_tot}/{q_rid}) e compimento della missione dell'Anima[cite: 3].
"""

                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[{"role": "user", "content": prompt}],
                        temperature=0.2
                    )

                    st.subheader("📖 Profilo Numerologico Narrativo ed Evolutivo")
                    st.markdown(response.choices[0].message.content)

                except Exception as e:
                    st.error(f"Si è verificato un errore: {e}")
        else:
            st.warning("Compila tutti i campi.")
