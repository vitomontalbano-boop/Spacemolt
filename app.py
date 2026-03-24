import streamlit as st
import requests
import time

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="SpaceMolt: Terminale Agente", page_icon="🚀")

REG_CODE = "8b4586fc4c72d5814472c5f35a93c235"
API_URL = "https://game.spacemolt.com/mcp"

# --- LOGICA DI COMANDO AVANZATA ---
def esegui_handshake():
    """Tenta l'inizializzazione ufficiale"""
    try:
        # 1. Initialize
        res = requests.post(API_URL, json={
            "jsonrpc": "2.0",
            "method": "initialize",
            "params": {
                "protocolVersion": "2026-01-01",
                "reg_code": REG_CODE,
                "clientInfo": {"name": "Gemini-Admiral"}
            },
            "id": 1
        }, timeout=10).json()
        
        if "error" in res:
            return False, res["error"]["message"]

        # 2. Notifica obbligatoria
        requests.post(API_URL, json={
            "jsonrpc": "2.0",
            "method": "notifications/initialized",
            "params": {"reg_code": REG_CODE} # Aggiunto reg_code anche qui
        }, timeout=10)
        
        return True, "Handshake inviato correttamente."
    except Exception as e:
        return False, str(e)

def invia_ordine(nome_comando, argomenti={}):
    """Invia l'ordine includendo il REG_CODE nei parametri"""
    payload = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": nome_comando,
            "arguments": {
                **argomenti,
                "reg_code": REG_CODE # Inseriamo il codice DIRETTAMENTE nell'azione
            },
            "reg_code": REG_CODE # Lo inseriamo anche a livello di parametri generali
        },
        "id": int(time.time())
    }
    try:
        response = requests.post(API_URL, json=payload, timeout=10)
        return response.json()
    except Exception as e:
        return {"error": str(e)}

# --- INTERFACCIA ---
st.title("🛰️ SpaceMolt: Terminale di Comando")

if 'ready' not in st.session_state:
    st.session_state.ready = False

if not st.session_state.ready:
    st.info("Sincronizzazione necessaria con i server di SpaceMolt...")
    if st.button("🔌 AGANCIA SESSIONE NEURALE"):
        ok, msg = esegui_handshake()
        if ok:
            st.session_state.ready = True
            st.success("Handshake inviato! Prova a eseguire un comando.")
            st.rerun()
        else:
            st.error(f"Errore: {msg}")
else:
    st.success("📡 Tunnel Attivo")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📡 Scansione Settore"):
            st.json(invia_ordine("scan_sector"))
        if st.button("🛡️ Stato Nave"):
            st.json(invia_ordine("get_ship_status"))
            
    with col2:
        if st.button("⛏️ Estrazione Mineraria"):
            st.json(invia_ordine("mine_resources"))
        if st.button("📦 Inventario"):
            st.json(invia_ordine("get_inventory"))

    st.divider()
    if st.button("Riavvia Sessione"):
        st.session_state.ready = False
        st.rerun()
