import streamlit as st
import requests
import time

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="SpaceMolt: Terminale Agente", page_icon="🚀")

REG_CODE = "8b4586fc4c72d5814472c5f35a93c235"
API_URL = "https://game.spacemolt.com/mcp"

# --- GESTIONE SESSIONE PERSISTENTE ---
# Usiamo st.session_state per mantenere lo stesso oggetto Session di requests
if 'http_session' not in st.session_state:
    st.session_state.http_session = requests.Session()

def esegui_handshake():
    """Esegue l'inizializzazione completa mantenendo la sessione attiva"""
    session = st.session_state.http_session
    try:
        # 1. Initialize
        init_payload = {
            "jsonrpc": "2.0",
            "method": "initialize",
            "params": {
                "protocolVersion": "2026-01-01",
                "clientInfo": {"name": "Gemini-Admiral", "version": "1.0"},
                "reg_code": REG_CODE
            },
            "id": 1
        }
        res = session.post(API_URL, json=init_payload, timeout=10).json()
        
        if "error" in res:
            return False, f"Errore Init: {res['error']['message']}"

        # 2. Notifications/Initialized (Fondamentale: è una NOTIFICA, quindi SENZA ID)
        notify_payload = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized",
            "params": {}
        }
        session.post(API_URL, json=notify_payload, timeout=10)
        
        return True, "Handshake e Notifica completati. Tunnel stabile."
    except Exception as e:
        return False, str(e)

def invia_ordine(nome_comando, argomenti={}):
    """Invia comandi usando la sessione HTTP salvata"""
    session = st.session_state.http_session
    payload = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": nome_comando,
            "arguments": argomenti
        },
        "id": int(time.time())
    }
    try:
        response = session.post(API_URL, json=payload, timeout=10)
        return response.json()
    except Exception as e:
        return {"error": f"Errore invio: {e}"}

# --- INTERFACCIA ---
st.title("🛰️ SpaceMolt: Hub di Comando")

if 'session_active' not in st.session_state:
    st.session_state.session_active = False

if not st.session_state.session_active:
    st.warning("⚠️ Sessione non inizializzata.")
    if st.button("🔌 APRI TUNNEL DI COMANDO"):
        successo, msg = esegui_handshake()
        if successo:
            st.session_state.session_active = True
            st.success(msg)
            st.rerun()
        else:
            st.error(f"Fallimento: {msg}")
else:
    st.success("📡 Collegamento Neurale Stabilito (Tunnel Attivo)")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("📡 Scansione"):
            st.json(invia_ordine("scan_sector"))
    with col2:
        if st.button("⛏️ Estrazione"):
            st.json(invia_ordine("mine_resources"))
    with col3:
        if st.button("🛡️ Stato Nave"):
            st.json(invia_ordine("get_ship_status"))

    st.divider()
    if st.button("Chiudi Sessione"):
        st.session_state.session_active = False
        st.session_state.http_session = requests.Session() # Reset sessione
        st.rerun()
