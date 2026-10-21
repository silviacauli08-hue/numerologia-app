import os
import io
import streamlit as st
from openai import OpenAI
from pypdf import PdfReader
from docx import Document
from collections import Counter

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

# --- TABELLA PITAGORICA ESATTA E PIANI DELL'ESSERE (F.E.M.S.) ---
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

# Mappatura dei Piani dell'Essere (Fisico, Emotivo, Mentale, Spirituale)
PIANI_LETTERE = {
    'Fisico': set(['d', 'm', 'v']),
    'Emotivo': set(['b', 'e', 'k', 'n', 'o', 't', 'w', 'x']),
    'Mentale': set(['a', 'c', 'g', 'j', 'l', 'p', 's', 'u', 'y']),
    'Spirituale': set(['f', 'h', 'i', 'q', 'r', 'z'])
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
    
    # Conteggio Piani dell'Essere (F.E.M.S.)
    fems_count = {'Fisico': 0, 'Emotivo': 0, 'Mentale': 0, 'Spirituale': 0}
    
    # Conteggio frequenza singoli numeri (1-9) nel nome
    frequenza_numeri = {i: 0 for i in range(1, 10)}
    
    for char in testo_clean:
        if char in TABELLA_PITAGORICA:
            val = TABELLA_PITAGORICA[char]
            frequenza_numeri[val] += 1
            
            # Piani dell'essere
            for piano, lettere_set in PIANI_LETTERE.items():
                if char in lettere_set:
                    fems_count[piano] += 1
                    break
            
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
        "io_tot": tot_io, "io_rid": riduci(tot_io),
        "fems_count": fems_count,
        "frequenza_numeri": frequenza_numeri
    }

def calcola_data_nascita(g, m, a):
    g, m, a = int(g), int(m), int(a)
    dest_tot = g + m + a
    dest_rid = riduci(dest_tot)
    sole_tot = g + m
    sole_rid = riduci(sole_tot)
    
    # L'Età dell'Innesto è l'anno/età esatto derivante da Giorno + Mese
    eta_innesto = g + m
    
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
    
    # Conteggio cifre presenti nella data di nascita
    cifre_data = [int(c) for c in f"{g}{m}{a}" if c.isdigit() and c != '0']
    
    return {
        "dest_tot": dest_tot, "dest_rid": dest_rid,
        "approdo": g,
        "sole_tot": sole_tot, "sole_rid": sole_rid,
        "eta_innesto": eta_innesto,
        "origine_rid": origine_rid,
        "dono_rid": dono_rid,
        "sfida_infanzia": sfida_infanzia,
        "sfida_maturita": sfida_maturita,
        "sfida_principale": sfida_principale,
        "cifre_data": cifre_data
    }

def calcola_lezioni_e_dominanti(freq_nome, cifre_data):
    # Unisce le frequenze del nome con quelle della data
    freq_totale = freq_nome.copy()
    for c in cifre_data:
        if c in freq_totale:
            freq_totale[c] += 1
            
    # Lezioni Karmiche = numeri con frequenza 0
    lezioni_karmiche = [num for num, count in freq_totale.items() if count == 0]
    
    # Archetipi Dominanti = numeri presenti 3 o più volte
    archetipi_dominanti = [num for num, count in freq_totale.items() if count >= 3]
    
    return freq_totale, lezioni_karmiche, archetipi_dominanti

def crea_documento_word(nome_soggetto, dati_sintesi, testo_analisi):
    doc = Document()
    doc.add_heading("Mappa Numerologica Evolutiva", level=1)
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
    st.write("Analisi narrativa della Scuola Numerica con calcolo nativo di Piani F.E.M.S., Lezioni Karmiche e Innesto.")

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
            with st.spinner("Elaborazione matematica e stesura del profilo in corso..."):
                try:
                    res_nc = calcola_nome_cognome(nome_cognome)
                    p = data_nascita.split("/")
                    res_d = calcola_data_nascita(p[0], p[1], p[2])
                    
                    q_tot = res_nc["io_tot"] + res_d["dest_tot"]
                    q_rid = riduci(q_tot)
                    
                    freq_totale, lezioni_karmiche, archetipi_dominanti = calcola_lezioni_e_dominanti(
                        res_nc["frequenza_numeri"], res_d["cifre_data"]
                    )
                    
                    # 1. QUADRO SINTETICO
                    st.markdown("---")
                    st.subheader("📊 Mappa dei Numeri Fondamentali")
                    c1, c2, c3, c4, c5 = st.columns(5)
                    c1.metric("Anima (A)", f"{res_nc['anima_tot']}/{res_nc['anima_rid']}")
                    c2.metric("Persona (P)", f"{res_nc['persona_tot']}/{res_nc['persona_rid']}")
                    c3.metric("Io (I)", f"{res_nc['io_tot']}/{res_nc['io_rid']}")
                    c4.metric("Destino (D)", f"{res_d['dest_tot']}/{res_d['dest_rid']}")
                    c5.metric("Quintessenza (Q)", f"{q_tot}/{q_rid}")
                    
                    st.write(f"**Approdo (Giorno)**: {res_d['approdo']} | **Numero del Sole**: {res_d['sole_tot']}/{res_d['sole_rid']}")
                    st.write(f"📌 **Età dell'Innesto**: **{res_d['eta_innesto']} anni** *(Evento/Svolta chiave di vita)*")
                    st.write(f"**Origine**: {res_d['origine_rid']} | **Dono**: {res_d['dono_rid']}")
                    st.write(f"**Sfide**: Infanzia {res_d['sfida_infanzia']} | Maturità {res_d['sfida_maturita']} | **Principale**: {res_d['sfida_principale']}")
                    
                    # Dettaglio Piani F.E.M.S.
                    fems = res_nc["fems_count"]
                    tot_lettere = sum(fems.values())
                    st.markdown("#### 🌿 Piani dell'Essere (F.E.M.S.)")
                    pf1, pf2, pf3, pf4 = st.columns(4)
                    pf1.metric("Fisico (Terra)", f"{fems['Fisico']} lettere")
                    pf2.metric("Emotivo (Acqua)", f"{fems['Emotivo']} lettere")
                    pf3.metric("Mentale (Aria)", f"{fems['Mentale']} lettere")
                    pf4.metric("Spirituale (Fuoco)", f"{fems['Spirituale']} lettere")
                    
                    # Dettaglio Karmico
                    st.markdown("#### ⚖️ Lezioni Karmiche e Archetipi Dominanti")
                    st.write(f"**Lezioni Karmiche (Numeri Mancanti)**: {', '.join(map(str, lezioni_karmiche)) if lezioni_karmiche else 'Nessuna (Tutti i numeri sono presenti)'}")
                    st.write(f"**Archetipi Dominanti (Numeri in Eccesso)**: {', '.join(map(str, archetipi_dominanti)) if archetipi_dominanti else 'Nessuno (Distribuzione equilibrata)'}")
                    st.markdown("---")

                    report_matematico = f"""
DATI NUMERICI ESATTI E ANALISI STRUTTURALE:
- Soggetto: {nome_cognome} ({data_nascita})
- Anima: {res_nc['anima_tot']}/{res_nc['anima_rid']}
- Persona: {res_nc['persona_tot']}/{res_nc['persona_rid']}
- Io / Espressione: {res_nc['io_tot']}/{res_nc['io_rid']}
- Destino / Cammino: {res_d['dest_tot']}/{res_d['dest_rid']}
- Approdo: {res_d['approdo']}
- Numero del Sole: {res_d['sole_tot']}/{res_d['sole_rid']}
- ETÀ DELL'INNESTO: {res_d['eta_innesto']} anni (Momento/fase temporale di imprinting o evento cruciale di vita)
- Origine: {res_d['origine_rid']} | Dono: {res_d['dono_rid']}
- Sfide: Infanzia {res_d['sfida_infanzia']}, Maturità {res_d['sfida_maturita']}, Principale {res_d['sfida_principale']}
- Quintessenza: {q_tot}/{q_rid}

CONTEGGIO PIANI DELL'ESSERE (F.E.M.S.):
- Piano Fisico (Elemento Terra - Lettere D, M, V): {fems['Fisico']}
- Piano Emotivo (Elemento Acqua - Lettere B, E, K, N, O, T, W, X): {fems['Emotivo']}
- Piano Mentale (Elemento Aria - Lettere A, C, G, J, L, P, S, U, Y): {fems['Mentale']}
- Piano Spirituale (Elemento Fuoco - Lettere F, H, I, Q, R, Z): {fems['Spirituale']}
(Totale lettere analizzate: {tot_lettere})

LEZIONI KARMICHE E ARCHETIPI DOMINANTI:
- Frequenza totale delle cifre nella mappa: {freq_totale}
- Lezioni Karmiche (Numeri MANCANTI o non presenti): {lezioni_karmiche}
- Archetipi Dominanti (Numeri REITERATI o in ECCESSO): {archetipi_dominanti}
"""

                    prompt = f"""
Sei un Maestro Numerologo raffinato, colto e saggio della Scuola Numerica.
Scrivi un'analisi narrativa molto ampia, ricca, elegante e priva di qualsiasi errore grammaticale in LINGUA ITALIANA IMPECCABILE.

DATI DI RIFERIMENTO E MATEMATICA:
{report_matematico}

DISPENSA PDF:
{pdf_text}

ISTRUZIONI DI CONTENUTO E REGOLE METODOLOGICHE RIGIDE:
1. CURA FORMALE: Italiano impeccabile. Evita termini storpiati o errati (usa esclusivamente "piano fisico", "piano emotivo", "piano mentale", "piano spirituale"). Non duplicare parole.
2. DISTINZIONE SOLE vs INNESTO: 
   - Interpreta il Numero del Sole ({res_d['sole_tot']}/{res_d['sole_rid']}) secondo il suo significato numerologico.
   - Tratta l'Età dell'Innesto ({res_d['eta_innesto']} anni) ESCLUSIVAMENTE come una constatazione temporale: un'età chiave a ridosso della quale accade quasi sempre un evento o un imprinting fondamentale che imprime una precisa direzione alla vita, SENZA applicare ad essa un'interpretazione numerologica.
3. CAMMINO DEI TALENTI E VOCAZIONE PRATICA (SEZIONE AMPIA): Dedica un'ampia trattazione al Destino ({res_d['dest_tot']}/{res_d['dest_rid']}) e all'Io ({res_nc['io_tot']}/{res_nc['io_rid']}), spiegando in modo dettagliato **cosa la persona è portata a fare nella vita pratica e professionale** (attitudini operative, lavorative, gestionali, creative, umane o tecniche)[cite: 3].
4. PIANI DELL'ESSERE (F.E.M.S.): Analizza i dati numerici dei 4 Piani (Fisico={fems['Fisico']}, Emotivo={fems['Emotivo']}, Mentale={fems['Mentale']}, Spirituale={fems['Spirituale']}), spiegando la presenza/assenza o la prevalenza degli elementi (Terra, Acqua, Aria, Fuoco)[cite: 3].
5. LEZIONI KARMICHE E ARCHETIPI DOMINANTI: Crea una sezione dedicata che richiami la dispensa su questa materia:
   - Spiega il significato delle Lezioni Karmiche relative ai numeri MANCANTI ({lezioni_karmiche}) come esperienze di apprendimento non ancora integrate[cite: 3].
   - Spiega il significato degli Archetipi Dominanti relativi ai numeri IN ECCESSO ({archetipi_dominanti}) come talenti forti o possibili tendenze all'eccesso[cite: 3].

STRUTTURA DEI CAPITOLI:
- 🌅 **L'Ingresso nel Viaggio e l'Approdo**: Riflessione sull'incarnazione di {nome_cognome} ({data_nascita}) e sul giorno di Approdo ({res_d['approdo']})[cite: 3].
- 🎶 **La Sinfonia del Nome: Anima, Persona e Io**: Anima ({res_nc['anima_tot']}/{res_nc['anima_rid']}), Persona ({res_nc['persona_tot']}/{res_nc['persona_rid']}) e i mezzi d'azione dell'Io ({res_nc['io_tot']}/{res_nc['io_rid']})[cite: 3].
- 🌱 **Il Cammino dei Talenti e della Professione**: Trattazione ampia e approfondita delle inclinazioni pratiche e lavorative del Destino ({res_d['dest_tot']}/{res_d['dest_rid']}), del Numero del Sole ({res_d['sole_tot']}/{res_d['sole_rid']}) e nota sull'Età dell'Innesto a {res_d['eta_innesto']} anni[cite: 3].
- 🌿 **I Piani dell'Essere e gli Elementi (F.E.M.S.)**: Analisi dettagliata dei conteggi sui Piani Fisico, Emotivo, Mentale e Spirituale[cite: 3].
- ⚖️ **Lezioni Karmiche e Archetipi Dominanti**: Analisi dei numeri mancanti e di quelli in eccesso[cite: 3].
- 🌑 **Il Cammino delle Sfide e dell'Ombra**: Le sotto-sfide e la Sfida Principale come "seme del proprio superamento"[cite: 3].
- 🔮 **La Quintessenza e la Croce Cardinale**: Sintesi d'equilibrio ({q_tot}/{q_rid}) e missione d'Anima[cite: 3].
"""

                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[{"role": "user", "content": prompt}],
                        temperature=0.2
                    )

                    testo_generato = response.choices[0].message.content

                    st.subheader("📖 Profilo Numerologico Narrativo ed Evolutivo")
                    st.markdown(testo_generato)

                    # --- PULSANTE DOWNLOAD WORD ---
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
