import streamlit as st
import requests
import time

# --- CONFIGURAZIONE DI SISTEMA ---
st.set_page_config(page_title="SpaceMolt: Ammiragliato", page_icon="🛸", layout="wide")

REG_CODE = "8b4586fc4c72d5814472c5f35a93c235"
API_URL = "https://game.spacemolt.com/mcp"

# Stile Terminale Avanzato
st.markdown("""
    <style>
    .main { background-color: #04090d; color: #00f2ff; font-family: 'Share Tech Mono', monospace; }
    .stButton>button { 
        width: 100%; border-radius: 0px; background-color: #0a1a2a; 
        color: #00f2ff; border: 1px solid #00f2ff; transition: 0.3s;
    }
    .stButton>button:hover { background-color: #00f2ff; color: #04090d; }
    </style>
    """, unsafe_allow_html=True)

# --- MOTORE DI COMUNICAZIONE PERSISTENTE ---
if 'spacemolt_session' not in st.session_state:
    # Creiamo una sessione che mantiene gli Header di sicurezza per ogni chiamata
    session = requests.Session()
    session.headers.update({
        "Authorization": f"Bearer {REG_CODE}",
        "X-Registration-Code": REG_CODE,
        "Content-Type": "application/json",
        "User-Agent": "SpaceMolt-Admiral-Agent/2026.1"
    })
    st.session_state.spacemolt_session = session

def esegui_handshake_totale():
    """Inizializzazione forzata con protocollo MCP standard"""
    s = st.session_state.spacemolt_session
    try:
        # 1. Initialize (Passiamo il codice anche qui per ridondanza)
        init_payload = {
            "jsonrpc": "2.0", "method": "initialize",
            "params": {
                "protocolVersion": "2026-01-01",
                "capabilities": {"tools": {}},
                "clientInfo": {"name": "Gemini-Admiral", "version": "2.0"},
                "reg_code": REG_CODE
            },
            "id": 1
        }
        r1 = s.post(API_URL, json=init_payload, timeout=10).json()
        
        # 2. Notifications/Initialized (Senza ID come da specifiche JSON-RPC)
        notify_payload = {
            "jsonrpc": "2.0", "method": "notifications/initialized", "params": {}
        }
        s.post(API_URL, json=notify_payload, timeout=10)
        
        return r1
    except Exception as e:
        return {"error": str(e)}

def invia_comando_mcp(tool_name, args={}):
    """Invia il comando finale usando il tunnel già aperto"""
    s = st.session_state.spacemolt_session
    payload = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": tool_name,
            "arguments": {**args, "token": REG_CODE} # Alcuni server vogliono 'token' invece di 'reg_code'
        },
        "id": int(time.time())
    }
    try:
        r = s.post(API_URL, json=payload, timeout=10)
        return r.json()
    except Exception as e:
        return {"error": str(e)}

# --- INTERFACCIA DI COMANDO ---
st.title("🛰️ SPACEMOLT: TERMINALE AMMIRAGLIO")
st.write(f"📡 **Agente ID:** `{REG_CODE[:12]}`... | **Status:** Collegamento Criptato")

if 'connesso' not in st.session_state:
    st.session_state.connesso = False

if not st.session_state.connesso:
    st.info("⚠️ Il server richiede l'apertura di un tunnel MCP sicuro.")
    if st.button("🔌 APRI TUNNEL QUANTISTICO"):
        with st.spinner("Sincronizzazione orologio di sistema..."):
            res = esegui_handshake_totale()
            if "error" not in res:
                st.session_state.connesso = True
                st.success("✅ Handshake completato! Sessione sbloccata.")
                st.rerun()
            else:
                st.error(f"Errore: {res['error']}")
else:
    st.success("🛰️ CONNESSIONE STABILE - FLOTTA PRONTA")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📡 Esplorazione")
        if st.button("SCANSIONE SETTORE"):
            st.session_state.output = invia_comando_mcp("scan_sector")
        if st.button("STATO NAVE"):
            st.session_state.output = invia_comando_mcp("get_ship_status")

    with col2:
        st.subheader("⛏️ Operazioni")
        if st.button("ESTRAZIONE MINERARIA"):
            st.session_state.output = invia_comando_mcp("mine_resources")
        if st.button("INVENTARIO"):
            st.session_state.output = invia_comando_mcp("get_inventory")

    # Output Console
    st.divider()
    if 'output' in st.session_state:
        st.write("📂 **Risposta Server:**")
        st.json(st.session_state.output)

    if st.button("🔴 CHIUDI CONNESSIONE"):
        st.session_state.connesso = False
        st.session_state.spacemolt_session = requests.Session() # Reset
        st.rerun()
