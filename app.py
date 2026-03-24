import streamlit as st
import requests
import time

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="SpaceMolt Admiral", page_icon="🛸")

REG_CODE = "8b4586fc4c72d5814472c5f35a93c235"
API_URL = "https://game.spacemolt.com/mcp"

# Stile Ultra-Minimal per Android
st.markdown("""
    <style>
    .main { background-color: #000; color: #00ff41; font-family: monospace; }
    .stButton>button { 
        width: 100%; height: 4em; background-color: #003300; 
        color: #00ff41; border: 1px solid #00ff41; font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# --- MOTORE DI COMUNICAZIONE "FLASH" ---
def esegui_azione_totale(nome_comando):
    """Esegue Handshake + Comando in un'unica sessione HTTP persistente"""
    s = requests.Session()
    # Header specifici per il protocollo SpaceMolt 2026
    s.headers.update({
        "Authorization": f"Bearer {REG_CODE}",
        "X-SpaceMolt-Token": REG_CODE,
        "Content-Type": "application/json"
    })

    try:
        # 1. INITIALIZE
        s.post(API_URL, json={
            "jsonrpc": "2.0", "method": "initialize",
            "params": {"protocolVersion": "2026-01-01", "reg_code": REG_CODE},
            "id": 1
        }, timeout=5)

        # 2. NOTIFICATIONS/INITIALIZED
        s.post(API_URL, json={
            "jsonrpc": "2.0", "method": "notifications/initialized",
            "params": {"reg_code": REG_CODE}
        }, timeout=5)

        # 3. IL VERO COMANDO (L'azione scelta dall'utente)
        payload = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": nome_comando,
                "arguments": {"reg_code": REG_CODE}
            },
            "id": int(time.time())
        }
        
        r = s.post(API_URL, json=payload, timeout=10)
        return r.json()

    except Exception as e:
        return {"error": f"Errore Link: {e}"}

# --- INTERFACCIA ---
st.title("🛰️ SpaceMolt Admiral")
st.write(f"📡 Link: `ATTIVO` | ID: `{REG_CODE[:8]}`")

st.divider()

# Griglia di comando per Android
col1, col2 = st.columns(2)

with col1:
    if st.button("📡 SCANSIONE"):
        res = esegui_azione_totale("scan_sector")
        st.session_state.last_op = res

    if st.button("🛡️ NAVE"):
        res = esegui_azione_totale("get_ship_status")
        st.session_state.last_op = res

with col2:
    if st.button("⛏️ ESTRAZIONE"):
        res = esegui_azione_totale("mine_resources")
        st.session_state.last_res = res

    if st.button("📦 CARGO"):
        res = esegui_azione_totale("get_inventory")
        st.session_state.last_op = res

# Display Risultati
if 'last_op' in st.session_state:
    st.divider()
    st.subheader("📂 Dati Ricevuti")
    st.json(st.session_state.last_op)
