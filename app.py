import streamlit as st
import requests
import time

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="SpaceMolt: Admiral", page_icon="🚀")

REG_CODE = "8b4586fc4c72d5814472c5f35a93c235"
# Inseriamo il codice direttamente nel tunnel URL per bypassare i blocchi di sessione
API_URL = f"https://game.spacemolt.com/mcp?reg_code={REG_CODE}"

# Stile Terminale
st.markdown("<style>.main { background-color: #020508; color: #00ff41; }</style>", unsafe_allow_html=True)

# --- MOTORE DI COMUNICAZIONE ---
def esegui_mcp(metodo, params_extra={}):
    """Invia una singola chiamata JSON-RPC pulita"""
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {REG_CODE}",
        "X-SpaceMolt-Auth": REG_CODE
    }
    
    payload = {
        "jsonrpc": "2.0",
        "method": metodo,
        "params": {**params_extra, "reg_code": REG_CODE},
        "id": int(time.time())
    }
    
    try:
        response = requests.post(API_URL, json=payload, headers=headers, timeout=10)
        return response.json()
    except Exception as e:
        return {"error": str(e)}

# --- LOGICA DI CONNESSIONE ---
def sequenza_handshake():
    """Inizializza e conferma in due passi rapidi"""
    # 1. Initialize
    st.write("📡 *Inviando segnale di inizializzazione...*")
    res1 = esegui_mcp("initialize", {
        "protocolVersion": "2026-01-01",
        "clientInfo": {"name": "Admiral-Gen"}
    })
    
    if "error" in res1:
        return res1
        
    # 2. Notifications/Initialized (Pura notifica)
    st.write("🛰️ *Sincronizzazione completata.*")
    requests.post(API_URL, json={
        "jsonrpc": "2.0",
        "method": "notifications/initialized",
        "params": {"reg_code": REG_CODE}
    })
    return res1

# --- INTERFACCIA ---
st.title("🛸 SpaceMolt: Terminale di Bordo")

if 'session_ok' not in st.session_state:
    st.session_state.session_ok = False

if not st.session_state.session_ok:
    if st.button("🔌 STABILISCI LINK NEURALE"):
        res = sequenza_handshake()
        if "error" not in res:
            st.session_state.session_ok = True
            st.success("Connessione stabilita!")
            st.rerun()
        else:
            st.error(f"Errore: {res['error']}")
else:
    st.success("📡 FLOTTA COLLEGATA")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📡 SCANSIONE RADAR"):
            # Dopo l'handshake, chiamiamo il tool
            st.session_state.last_data = esegui_mcp("tools/call", {"name": "scan_sector"})
            
    with col2:
        if st.button("🛡️ STATO NAVE"):
            st.session_state.last_data = esegui_mcp("tools/call", {"name": "get_ship_status"})

    if 'last_data' in st.session_state:
        st.divider()
        st.subheader("📊 Risposta Server")
        st.json(st.session_state.last_data)

    if st.button("RESET"):
        st.session_state.session_ok = False
        st.rerun()
