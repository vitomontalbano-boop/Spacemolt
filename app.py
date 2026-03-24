import streamlit as st
import requests
import time

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="SpaceMolt: Terminale Admiral", page_icon="🚀")

REG_CODE = "8b4586fc4c72d5814472c5f35a93c235"
API_URL = "https://game.spacemolt.com/mcp"

# Stile interfaccia
st.markdown("<style>.main { background-color: #020408; color: #00d4ff; font-family: 'Courier New'; }</style>", unsafe_allow_html=True)

# --- IL MOTORE "TRIPLE-TAP" ---
def esegui_missione_completa(nome_comando, argomenti={}):
    """Esegue l'intera sequenza richiesta dal server in un unico ciclo"""
    try:
        # 1. INITIALIZE
        init_res = requests.post(API_URL, json={
            "jsonrpc": "2.0",
            "method": "initialize",
            "params": {
                "protocolVersion": "2026-01-01",
                "reg_code": REG_CODE,
                "clientInfo": {"name": "Gemini-Admiral"}
            },
            "id": 1
        }, timeout=10).json()
        
        if "error" in init_res:
            return init_res

        # 2. NOTIFICATIONS/INITIALIZED
        requests.post(API_URL, json={
            "jsonrpc": "2.0",
            "method": "notifications/initialized",
            "params": {"reg_code": REG_CODE}
        }, timeout=10)

        # 3. IL VERO COMANDO (TOOLS/CALL)
        payload_comando = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": nome_comando,
                "arguments": {**argomenti, "reg_code": REG_CODE}
            },
            "id": int(time.time())
        }
        
        final_res = requests.post(API_URL, json=payload_comando, timeout=10).json()
        return final_res

    except Exception as e:
        return {"error": f"Errore di sistema: {e}"}

# --- INTERFACCIA UTENTE ---
st.title("🛰️ SpaceMolt: Comando Strategico")
st.write(f"**ID Sessione Attivo:** `{REG_CODE[:12]}...`")

st.divider()

# Pannello Comandi Diretti
st.subheader("🕹️ Console di Pilotaggio")
col1, col2 = st.columns(2)

with col1:
    if st.button("📡 SCANSIONE SETTORE"):
        with st.spinner("Sincronizzazione handshake..."):
            risultato = esegui_missione_completa("scan_sector")
            st.session_state.output = risultato

    if st.button("🛡️ STATO NAVE"):
        with st.spinner("Interrogazione sistemi..."):
            risultato = esegui_missione_completa("get_ship_status")
            st.session_state.output = risultato

with col2:
    if st.button("⛏️ ESTRAZIONE MINERARIA"):
        with st.spinner("Attivazione laser..."):
            risultato = esegui_missione_completa("mine_resources")
            st.session_state.output = risultato

    if st.button("📦 INVENTARIO STIVA"):
        with st.spinner("Controllo cargo..."):
            risultato = esegui_missione_completa("get_inventory")
            st.session_state.output = risultato

st.divider()

# Visualizzazione Risultati
if 'output' in st.session_state:
    st.subheader("📊 Risposta dal Server")
    st.json(st.session_state.output)
    
    # Se il server risponde ancora con l'errore di sessione, proviamo il metodo LOGIN alternativo
    if isinstance(st.session_state.output, dict) and "error" in st.session_state.output:
        if "Session not initialized" in st.session_state.output["error"].get("message", ""):
            st.error("Il server richiede un metodo di LOGIN esplicito. Vuoi tentare il protocollo alternativo?")
            if st.button("🔑 TENTA LOGIN ALTERNATIVO"):
                login_res = requests.post(API_URL, json={
                    "jsonrpc": "2.0", "method": "login", 
                    "params": {"reg_code": REG_CODE}, "id": 99
                }).json()
                st.json(login_res)
