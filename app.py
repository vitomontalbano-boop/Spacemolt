import streamlit as st
import requests
import json
import time

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="SpaceMolt: Terminale Admiral", page_icon="🚀")

REG_CODE = "8b4586fc4c72d5814472c5f35a93c235"
API_URL = "https://game.spacemolt.com/mcp"

# Stile Terminale per visibilità su Android
st.markdown("""
    <style>
    .main { background-color: #000b00; color: #00ff41; font-family: monospace; }
    .stButton>button { width: 100%; background-color: #003300; color: #00ff41; border: 1px solid #00ff41; height: 3.5em; }
    pre { background-color: #001100 !important; color: #00ff41 !important; border: 1px solid #00ff41; }
    </style>
    """, unsafe_allow_html=True)

# --- MOTORE DI COMUNICAZIONE ---
def chiama_spacemolt(metodo, params):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {REG_CODE}"
    }
    payload = {
        "jsonrpc": "2.0",
        "method": metodo,
        "params": params,
        "id": int(time.time())
    }
    try:
        r = requests.post(API_URL, json=payload, headers=headers, timeout=10)
        return r.json(), r.cookies.get_dict(), r.headers
    except Exception as e:
        return {"error": str(e)}, {}, {}

# --- LOGICA DI AGGANCIO ---
st.title("🛰️ SpaceMolt: Link Neurale")

if 'session_token' not in st.session_state:
    st.session_state.session_token = None

# TASTO 1: IL VERO LOGIN (Diverso dai tentativi precedenti)
if st.button("🔌 1. INIZIALIZZA E AUTENTICA"):
    with st.spinner("Forzatura handshake..."):
        # Tentiamo il metodo 'initialize' ma leggiamo TUTTA la risposta
        res, cookies, headers = chiama_spacemolt("initialize", {
            "protocolVersion": "2026-01-01",
            "reg_code": REG_CODE,
            "clientInfo": {"name": "Gemini-Admiral"}
        })
        
        st.write("📡 **Risposta del Server (Debug):**")
        st.json(res)
        
        if "result" in res:
            st.success("✅ Handshake riuscito! Il server ha accettato il codice.")
            # Inviamo la notifica di conferma immediatamente
            chiama_spacemolt("notifications/initialized", {"reg_code": REG_CODE})
            st.session_state.session_token = "ACTIVE"
        else:
            st.error("❌ Il server ha risposto con un errore. Guarda il JSON sopra.")

# TASTO 2: COMANDO OPERATIVO (Solo se loggati)
st.divider()
if st.button("📡 2. SCANSIONE SETTORE (TEST)"):
    if not st.session_state.session_token:
        st.warning("Esegui prima il punto 1!")
    else:
        with st.spinner("Esecuzione comando..."):
            # Proviamo a passare il reg_code in 3 posti diversi per sicurezza
            res, _, _ = chiama_spacemolt("tools/call", {
                "name": "scan_sector",
                "arguments": {"reg_code": REG_CODE},
                "reg_code": REG_CODE
            })
            st.json(res)

# TASTO 3: METODO ALTERNATIVO (Se il punto 1 fallisce)
with st.expander("🛠️ Protocolli di Emergenza"):
    if st.button("🔑 Tenta metodo 'register'"):
        res, _, _ = chiama_spacemolt("register", {"reg_code": REG_CODE})
        st.json(res)
