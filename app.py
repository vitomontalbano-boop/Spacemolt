import streamlit as st
import requests
import time

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="SpaceMolt: Terminale Agente", page_icon="🚀")

REG_CODE = "8b4586fc4c72d5814472c5f35a93c235"
API_URL = "https://game.spacemolt.com/mcp"

# Stile Cyber-Terminal
st.markdown("""
    <style>
    .main { background-color: #050a0f; color: #00ff41; font-family: 'Courier New'; }
    .stButton>button { 
        width: 100%; border-radius: 4px; background-color: #002200; 
        color: #00ff41; border: 1px solid #00ff41; font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# --- SEQUENZA DI INIZIALIZZAZIONE (HANDSHAKE) ---
def esegui_handshake():
    """Esegue la sequenza: initialize -> notifications/initialized"""
    try:
        # 1. Chiamata di inizializzazione
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
        res = requests.post(API_URL, json=init_payload, timeout=5).json()
        
        if "error" in res:
            return False, res["error"]["message"]

        # 2. Notifica di completamento (Obbligatoria per sbloccare il server)
        notify_payload = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized",
            "params": {}
        }
        requests.post(API_URL, json=notify_payload, timeout=5)
        
        return True, "Handshake completato con successo!"
    except Exception as e:
        return False, str(e)

# --- FUNZIONE COMANDI ---
def invia_ordine(nome_comando, argomenti={}):
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
        response = requests.post(API_URL, json=payload, timeout=5)
        return response.json()
    except Exception as e:
        return {"error": str(e)}

# --- INTERFACCIA ---
st.title("🛰️ SpaceMolt: Hub di Comando")
st.write(f"**Codice Registrazione:** `{REG_CODE[:8]}...`")

if 'session_active' not in st.session_state:
    st.session_state.session_active = False

if not st.session_state.session_active:
    st.warning("⚠️ Sessione non inizializzata.")
    if st.button("🔌 AVVIA PROTOCOLLO DI CONNESSIONE"):
        successo, msg = esegui_handshake()
        if successo:
            st.session_state.session_active = True
            st.success(msg)
            st.rerun()
        else:
            st.error(f"Fallimento Handshake: {msg}")
else:
    st.success("📡 Collegamento Neurale Stabilito")
    
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
    
    # Sezione AI (Ammiraglio)
    ordine_libero = st.text_input("Comunica con l'Agente IA", placeholder="Es: Spostati verso l'asteroide più ricco")
    if st.button("ESEGUI ORDINE"):
        st.info(f"Ricevuto, Comandante. Sto elaborando la sequenza per: {ordine_libero}")

    if st.button("Termina Sessione"):
        st.session_state.session_active = False
        st.rerun()
