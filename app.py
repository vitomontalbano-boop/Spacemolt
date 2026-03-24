import streamlit as st
import requests
import time

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="Crimson Fleet: Recruitment", page_icon="🏴‍☠️")

# Il tuo codice di registrazione (NON CAMBIARE)
REG_CODE = "8b4586fc4c72d5814472c5f35a93c235"
API_URL = "https://game.spacemolt.com/mcp"

st.markdown("""
    <style>
    .main { background-color: #1a0000; color: #ff4444; font-family: 'Courier New'; }
    .stButton>button { 
        width: 100%; border: 1px solid #ff4444; background-color: #440000; 
        color: #ff4444; font-weight: bold; height: 4em;
    }
    </style>
    """, unsafe_allow_html=True)

# --- MOTORE DI COMUNICAZIONE ---
def chiama_mcp(metodo, params):
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
        r = requests.post(API_URL, json=payload, headers=headers, timeout=15)
        return r.json()
    except Exception as e:
        return {"error": str(e)}

# --- STATO SESSIONE ---
if 'session_id' not in st.session_state:
    st.session_state.session_id = None
if 'username' not in st.session_state:
    st.session_state.username = ""

st.title("🏴‍☠️ Reclutamento Pirata")

# --- FASE 1: REGISTRAZIONE (CORRETTA) ---
if not st.session_state.session_id:
    st.write("⚓️ *Comandante, inserisci il tuo nome di battaglia per forzare il blocco.*")
    user_input = st.text_input("Username Pirata", "Kaelen_Red")
    
    if st.button("🔴 REGISTRA NELLA FLOTTA"):
        with st.spinner("Bypassando i protocolli imperiali..."):
            # 1. Inizializzazione standard
            chiama_mcp("initialize", {
                "protocolVersion": "2026-01-01", 
                "registration_code": REG_CODE # Usiamo il nome completo anche qui
            })
            chiama_mcp("notifications/initialized", {})
            
            # 2. Registrazione con la chiave corretta: registration_code
            res = chiama_mcp("tools/call", {
                "name": "register",
                "arguments": {
                    "username": user_input,
                    "empire": "crimson",
                    "registration_code": REG_CODE # CHIAVE CORRETTA RICHIESTA DAL SERVER
                }
            })
            
            # Analisi risposta
            if "result" in res:
                # Alcuni server MCP restituiscono il risultato dentro un campo 'content'
                result_data = res["result"]
                
                # Se il server ci dà il session_id, siamo dentro!
                if "session_id" in str(result_data):
                    # Cerchiamo il session_id nel dizionario o nel testo
                    st.session_state.session_id = result_data.get("session_id")
                    st.session_state.username = user_input
                    st.success("✅ Sei dentro! Preparati all'abbordaggio.")
                    st.rerun()
                else:
                    st.error("❌ Il server ha accettato il codice ma non ha rilasciato un ID. Controlla i dati qui sotto:")
                    st.json(res)
            else:
                st.error("❌ Errore critico durante la registrazione.")
                st.json(res)

# --- FASE 2: PONTE DI COMANDO ---
else:
    st.subheader(f"🛸 Capitano: {st.session_state.username}")
    st.write(f"📡 **Sessione Attiva:** `{st.session_state.session_id}`")

    if st.button("📡 SCANSIONE SETTORE"):
        res = chiama_mcp("tools/call", {
            "name": "scan_sector",
            "arguments": {"session_id": st.session_state.session_id}
        })
        st.json(res)

    if st.button("🔴 LOGOUT"):
        st.session_state.session_id = None
        st.rerun()
