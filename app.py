import streamlit as st
import requests
import time

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="SpaceMolt: Admiral", page_icon="🚀")

REG_CODE = "8b4586fc4c72d5814472c5f35a93c235"
API_URL = "https://game.spacemolt.com/mcp"

# Stile Matrix/Terminal
st.markdown("<style>.main { background-color: #020508; color: #00ff41; font-family: 'Courier New'; }</style>", unsafe_allow_html=True)

# --- MOTORE DI CONNESSIONE STATO-PERSISTENTE ---
if 'mcp_session' not in st.session_state:
    st.session_state.mcp_session = requests.Session()
    st.session_state.session_id = None

def esegui_chiamata(metodo, params={}, is_notification=False):
    """Esegue una chiamata JSON-RPC gestendo il Session-ID negli Header"""
    s = st.session_state.mcp_session
    
    # Prepariamo gli Header
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {REG_CODE}"
    }
    # Se abbiamo un Session-ID salvato, lo iniettiamo
    if st.session_state.session_id:
        headers["X-Session-Id"] = st.session_state.session_id
        headers["Cookie"] = f"session_id={st.session_state.session_id}"

    payload = {
        "jsonrpc": "2.0",
        "method": metodo,
        "params": {**params, "reg_code": REG_CODE}
    }
    if not is_notification:
        payload["id"] = int(time.time() * 1000)

    try:
        response = s.post(API_URL, json=payload, headers=headers, timeout=10)
        
        # TENTATIVO DI CATTURA SESSIONE: Cerchiamo negli Header della risposta
        if "X-Session-Id" in response.headers:
            st.session_state.session_id = response.headers["X-Session-Id"]
        elif "Set-Cookie" in response.headers:
            # Estraiamo il cookie di sessione se presente
            cookie = response.headers["Set-Cookie"].split(';')[0]
            if "=" in cookie:
                st.session_state.session_id = cookie.split('=')[1]

        return response.json()
    except Exception as e:
        return {"error": str(e)}

# --- LOGICA DI AGGANCIO ---
def apri_connessione_totale():
    """Sequenza obbligatoria: Initialize -> Initialized"""
    st.write("📡 *Tentativo di Handshake...*")
    
    # 1. Initialize
    res_init = esegui_chiamata("initialize", {
        "protocolVersion": "2026-01-01",
        "clientInfo": {"name": "Admiral-Gen-Mobile"}
    })
    
    if "error" in res_init:
        return False, res_init["error"].get("message", "Errore ignoto")

    # 2. Notifications/Initialized (Pura notifica per confermare la sessione)
    time.sleep(0.5) # Piccolo delay per permettere al server di registrare il session_id
    esegui_chiamata("notifications/initialized", {}, is_notification=True)
    
    return True, "Tunnel Quantistico Aperto!"

# --- INTERFACCIA ---
st.title("🛸 SpaceMolt: Terminale Admiral")

if 'connesso' not in st.session_state:
    st.session_state.connesso = False

if not st.session_state.connesso:
    st.info("⚠️ Sistema offline. Inizializzare il link neurale.")
    if st.button("🔌 AGGANCIA SERVER"):
        successo, msg = apri_connessione_totale()
        if successo:
            st.session_state.connesso = True
            st.success(msg)
            st.rerun()
        else:
            st.error(f"Fallimento: {msg}")
else:
    st.success(f"📡 COLLEGATO | ID Sessione: {st.session_state.session_id or 'Temporaneo'}")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📡 SCANSIONE SETTORE"):
            st.session_state.data = esegui_chiamata("tools/call", {"name": "scan_sector"})
            
    with col2:
        if st.button("🛡️ STATO NAVE"):
            st.session_state.data = esegui_chiamata("tools/call", {"name": "get_ship_status"})

    if 'data' in st.session_state:
        st.divider()
        st.write("📂 **Risposta Flotta:**")
        st.json(st.session_state.data)

    if st.button("🔴 DISCONNETTI"):
        st.session_state.connesso = False
        st.session_state.session_id = None
        st.session_state.mcp_session = requests.Session()
        st.rerun()
