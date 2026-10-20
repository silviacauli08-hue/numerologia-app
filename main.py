import os
import io
import streamlit as st
from openai import OpenAI
from pypdf import PdfReader
from docx import Document

# Configurazione pagina
st.set_page_config(page_title="App di Numerologia Evolutiva", layout="centered")

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

def crea_documento_word(nome_soggetto, dati_sintesi, testo_analisi):
    doc = Document()
    doc.add_heading(f"Mappa Numerologica Evolutiva", level=1)
    doc.add_heading(f"Profilo di: {nome_soggetto}", level=2)
    
    doc.add_heading("Quadro Numerico", level=3)
    for riga in dati_sintesi.split("\n"):
        if riga.strip():
            doc.add_paragraph(riga)
            
    doc.add_heading("Analisi Dettagliata", level=3)
    doc.add_paragraph(testo_analisi)
    
    file_stream = io.BytesIO()
    doc.save(file_stream)
    file_stream.seek(0)
    return file_stream

if check_password():
    st.title("✨ Mappa Numerologica Evolutiva")
    st.write("Analisi narrativa profonda, orientata alla professione, ai piani dell'essere e con esportazione in Word.")

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
        nome_cognome = st.text_input("Nome e Cognome:", value="Giovanni Pittia")
    with col2:
        data_nascita = st.text_input("Data di Nascita (GG/MM/AAAA):", value="22/03/2009")

    if st.button("Genera Analisi Approfondita") and api_key:
        if nome_cognome and data_nascita:
            with st.spinner("Elaborazione del profilo e preparazione del file in corso..."):
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
- Anima: {res_nc['anima_tot']}/{res_nc['anima_rid']}
- Persona: {res_nc['persona_tot']}/{res_nc['persona_rid']}
- Io / Espressione: {res_nc['io_tot']}/{res_nc['io_rid']}
- Destino / Cammino: {res_d['dest_tot']}/{res_d['dest_rid']}
- Approdo: {res_d['approdo']}
- Sole / Forza: {res_d['sole_tot']}/{res_d['sole_rid']} (Innesto: {res_d['sole_tot']} anni)
- Origine: {res_d['origine_rid']} | Dono: {res_d['dono_rid']}
- Sotto-sfida Infanzia: {res_d['sfida_infanzia']}
- Sotto-sfida Maturità: {res_d['sfida_maturita']}
- Sfida Principale: {res_d['sfida_principale']}
- Quintessenza: {q_tot}/{q_rid}
"""

                    prompt = f"""
Sei un Maestro Numerologo saggio, colto e raffinato della Scuola Numerica. 
Scrivi un profilo numerologico narrativo molto ampio, ricco, fluido ed elegante in LINGUA ITALIANA CORRETTA E IMPECCABILE. 

REGOLE DI SCRITTURA RIGIDE:
1. CURA DELLA LINGUA: Scrivi esclusivamente in italiano formale e corretto. Evita in modo assoluto termini errati come "pianoforte" (usa esclusivamente "piano fisico", "piano emotivo", "piano mentale", "piano spirituale"). Non duplicare mai parole o sillabe.
2. AMPIEZZA DESCRITTIVA: Crea sezioni ampie, avvolgenti e dettagliate, senza elenchi puntati freddi. 
3. INCLINAZIONI PRATICHE E PROFESSIONALI: Spiega in modo approfondito ed esteso **cosa la persona è portata a fare nella vita pratica e professionale** in base ai suoi numeri chiave (in particolare per il Destino e l'Io), collegando l'energia del numero a sbocchi concreti (es. gestione, organizzazione e metodo per il 4; leadership o impresa per l'8; relazioni, empatia e mediazione per il 2; altruismo, educazione o sociale per il 9; ecc.).
4. PIANI DELL'ESSERE: Inserisci un capitolo dedicato ai **Piani dell'Essere e agli Elementi (F.E.M.S.)** spiegando con precisione la distribuzione e l'influenza dei piani fisico, emotivo, mentale e spirituale.

DATI DI RIFERIMENTO:
{report_matematico}

DISPENSA DI RIFERIMENTO:
{pdf_text}

STRUTTURA DEI CAPITOLI RICHIESTA:
- 🌅 **L'Ingresso nel Viaggio e l'Approdo**: Ampia riflessione sull'incarnazione di {nome_cognome} ({data_nascita}) e sul profondo significato alchemico del giorno di Approdo ({res_d['approdo']}).
- 🎶 **La Sinfonia del Nome: Anima, Persona e Io**: Analisi estesa del desiderio del cuore (Anima: {res_nc['anima_tot']}/{res_nc['anima_rid']}), dello scudo relazionale (Persona: {res_nc['persona_tot']}/{res_nc['persona_rid']}) e dei talenti operativi e professionali messi in campo dall'Io ({res_nc['io_tot']}/{res_nc['io_rid']}).
- 🌱 **Il Cammino dei Talenti e della Professione**: Trattazione ampia e dettagliata del Destino ({res_d['dest_tot']}/{res_d['dest_rid']}), esaminando approfonditamente le inclinazioni pratiche, le vocazioni lavorative e i contesti in cui la persona esprime al meglio il proprio potenziale. Approfondisci anche la Forza del Sole ({res_d['sole_tot']}/{res_d['sole_rid']}) con l'Innesto a {res_d['sole_tot']} anni, l'Origine e il Dono.
- 🌿 **I Piani dell'Essere e gli Elementi (F.E.M.S.)**: Trattazione dedicata dei piani energetici (Fisico/Terra, Emotivo/Acqua, Mentale/Aria, Spirituale/Fuoco) presenti nella struttura del nome.
- 🌑 **Il Cammino delle Sfide e dell'Ombra**: Analisi evolutiva della Sotto-sfida d'infanzia ({res_d['sfida_infanzia']}), di maturità ({res_d['sfida_maturita']}) e della Sfida Principale ({res_d['sfida_principale']}), viste come il "seme del proprio superamento".
- 🔮 **La Quintessenza e la Croce Cardinale**: Conclusione ampia e poetica incentrata sul centro d'equilibrio ({q_tot}/{q_rid}) e sul compimento della missione dell'Anima.
"""

                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[{"role": "user", "content": prompt}],
                        temperature=0.2
                    )

                    testo_generato = response.choices[0].message.content

                    st.subheader("📖 Profilo Numerologico Narrativo ed Evolutivo")
                    st.markdown(testo_generato)

                    # --- AGGIUNTA DEL PULSANTE DI DOWNLOAD WORD ---
                    st.markdown("---")
                    st.subheader("💾 Esporta la Mappa")
                    
                    docx_file = crea_documento_word(nome_cognome, report_matematico, testo_generato)
                    
                    st.download_button(
                        label="📥 Scarica Mappa in formato Word (.docx)",
                        data=docx_file,
                        file_name=f"Mappa_Numerologica_{nome_cognome.replace(' ', '_')}.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    )

                except Exception as e:
                    st.error(f"Si è verificato un errore: {e}")
        else:
            st.warning("Compila tutti i campi.")
