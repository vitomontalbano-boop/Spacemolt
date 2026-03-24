import streamlit as st
import requests
import time

# --- CONFIGURAZIONE DI BORDO ---
st.set_page_config(page_title="SpaceMolt: Terminale Agente", page_icon="🚀", layout="wide")

# Il tuo codice di registrazione univoco
REG_CODE = "8b4586fc4c72d5814472c5f35a93c235"
API_URL = "https://game.spacemolt.com/mcp"

# Stile Interfaccia (Cyberpunk/Terminal)
st.markdown("""
    <style>
    .main { background-color: #02060a; color: #00ff41; }
    .stButton>button { 
        width: 100%; border-radius: 2px; 
        background-color: #003300; color: #00ff41; 
        border: 1px solid #00ff41; font-family: 'Courier New';
    }
    .stTextInput>div>div>input { background-color: #001100; color: #00ff41; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNZIONI DI COMANDO ---
def invia_ordine(comando, parametri={}):
    """Invia un'istruzione al server centrale di SpaceMolt"""
    payload = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "reg_code": REG_CODE,
            "name": comando,
            "arguments": parametri
        },
        "id": int(time.time())
    }
    try:
        # Nota: Usiamo un timeout breve per risposte rapide tipiche del 2026
        response = requests.post(API_URL, json=payload, timeout=5)
        return response.json()
    except Exception as e:
        return {"error": f"Connessione persa: {e}"}

# --- INTERFACCIA DI COMANDO ---
st.title("🛰️ SpaceMolt: Hub Agente Autonomo")
st.write(f"**Stato Sistema:** 🟢 Collegato | **ID Agente:** {REG_CODE[:8]}...")

col1, col2 = st.columns([1, 2])

with col1:
    st.header("🕹️ Azioni Rapide")
    if st.button("📡 Scansione Settore"):
        res = invia_ordine("scan_sector")
        st.session_state.last_res = res
        
    if st.button("⛏️ Estrazione Risorse"):
        res = invia_ordine("mine_resources")
        st.session_state.last_res = res
        
    if st.button("🛡️ Stato Scudi"):
        res = invia_ordine("get_ship_status")
        st.session_state.last_res = res

with col2:
    st.header("📊 Output Sensori")
    if 'last_res' in st.session_state:
        st.json(st.session_state.last_res)
    else:
        st.info("In attesa di dati dal server di SpaceMolt...")

st.divider()

# --- INTEGRAZIONE CON ME (GEMINI) ---
st.header("🧠 Istruzioni per l'IA (Ammiraglio)")
comando_vocale = st.text_area("Cosa devo fare nella galassia?", 
                              placeholder="Esempio: Spostati nel sistema Molt-Gamma e vendi tutto il rame che hai.")

if st.button("ESEGUI MISSIONE"):
    with st.spinner("Analizzando rotte e mercati..."):
        # Qui io interpreto il tuo testo e potrei concatenare più chiamate API
        # Per ora simuliamo la conferma della missione
        st.success(f"Comandante, ho ricevuto l'ordine: '{comando_vocale}'. Avvio i motori a curvatura.")
        # Esempio di logica futura: invia_ordine("move", {"target": "Molt-Gamma"})
