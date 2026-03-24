import streamlit as st
import requests
import time

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="SpaceMolt: Admiral", page_icon="🚀")

REG_CODE = "8b4586fc4c72d5814472c5f35a93c235"
API_URL = "https://game.spacemolt.com/mcp"

# Stile Terminale Deep Space
st.markdown("""
    <style>
    .main { background-color: #000505; color: #00ffcc; font-family: 'Courier New'; }
    .stButton>button { 
        width: 100%; border: 1px solid #00ffcc; background-color: #001a1a; 
        color: #00ffcc; font-weight: bold; height: 3em;
    }
    </style>
    """, unsafe_allow_html=True)

# --- IL MOTORE "ATOMIC HANDSHAKE" ---
def esegui_ordine_spaziale(nome_tool, argomenti={}):
    """
    Esegue la sequenza completa in un unico flusso per ingannare il timeout del server.
    """
    # Usiamo un'unica sessione per questa specifica esecuzione
    s = requests.Session()
    s.headers.update({
        "Authorization": f"Bearer {REG_CODE}",
        "Content-Type": "application/json"
    })

    try:
        # 1. INITIALIZE (Il 'Ciao, sono io')
        s.post(API_URL, json={
            "jsonrpc": "2.0",
            "method": "initialize",
            "params": {
                "protocolVersion": "2026-01-01",
                "reg_code": REG_CODE,
                "clientInfo": {"name": "Admiral-Gen-Mobile"}
            },
            "id": 1
        }, timeout=10)

        # 2. NOTIFICATIONS/INITIALIZED (Il 'Ricevuto, sono pronto')
        # Nota: Molti server del 2026 vogliono questa notifica SENZA ID per confermare il tunnel
        s.post(API_URL, json={
            "jsonrpc": "2.0",
            "method": "notifications/initialized",
            "params": {}
        }, timeout=10)

        # 3. TOOLS/CALL (Il vero ordine)
        payload_finale = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": nome_tool,
                "arguments": {**argomenti, "reg_code": REG_CODE}
            },
            "id": int(time.time())
        }
        
        risposta = s.post(API_URL, json=payload_finale, timeout=10)
        return risposta.json()

    except Exception as e:
        return {"error": f"Errore di trasmissione: {e}"}

# --- INTERFACCIA DI COMANDO ---
st.title("🛸 SpaceMolt: Terminale Admiral")
st.write(f"📡 **Stato:** Pronto all'invio immediato | **Codice:** `{REG_CODE[:8]}...`")

st.divider()

col1, col2 = st.columns(2)

with col1:
    if st.button("📡 SCANSIONE SETTORE"):
        with st.spinner("Sincronizzazione handshake..."):
            res = esegui_ordine_spaziale("scan_sector")
            st.session_state.last_res = res
            
    if st.button("🛡️ STATO NAVE"):
        with st.spinner("Interrogazione telemetria..."):
            res = esegui_ordine_spaziale("get_ship_status")
            st.session_state.last_res = res

with col2:
    if st.button("⛏️ ESTRAZIONE MINERARIA"):
        with st.spinner("Attivazione laser..."):
            res = esegui_ordine_spaziale("mine_resources")
            st.session_state.last_res = res
            
    if st.button("📦 INVENTARIO CARGO"):
        with st.spinner("Scansione stiva..."):
            res = esegui_ordine_spaziale("get_inventory")
            st.session_state.last_res = res

# --- LOG DI COMUNICAZIONE ---
if 'last_res' in st.session_state:
    st.divider()
    st.subheader("📂 Dati Ricevuti")
    st.json(st.session_state.last_res)
