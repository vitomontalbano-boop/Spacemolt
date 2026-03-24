import streamlit as st
import requests
import time
import json

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="Crimson Fleet: Identity", page_icon="🏴‍☠️")

REG_CODE = "8b4586fc4c72d5814472c5f35a93c235"
API_URL = "https://game.spacemolt.com/mcp"

st.markdown("""
    <style>
    .main { background-color: #1a0000; color: #ff4444; font-family: 'Courier New'; }
    .stButton>button { 
        width: 100%; border: 1px solid #ff4444; background-color: #440000; 
        color: #ff4444; font-weight: bold; height: 3.5em;
    }
    .stTextInput>div>div>input { background-color: #2a0000; color: #ff4444; border: 1px solid #ff4444; }
    </style>
    """, unsafe_allow_html=True)

def chiama_mcp(metodo, params):
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {REG_CODE}"}
    payload = {"jsonrpc": "2.0", "method": metodo, "params": params, "id": int(time.time())}
    try:
        r = requests.post(API_URL, json=payload, headers=headers, timeout=15)
        return r.json()
    except Exception as e:
        return {"error": str(e)}

if 'session_id' not in st.session_state:
    st.session_state.session_id = None

st.title("🏴‍☠️ SpaceMolt: Reclutamento Pirata")

if not st.session_state.session_id:
    st.write("⚓️ *Il nome precedente era già occupato. Scegline uno nuovo, Ammiraglio!*")
    
    # Suggerimento: aggiungi numeri o caratteri speciali per renderlo unico
    nuovo_username = st.text_input("Inserisci il tuo nome da battaglia", placeholder="Es: Kaelen_Red_99 o Blood_Bucaneer")
    
    if st.button("🔴 FORZA REGISTRAZIONE"):
        with st.spinner("Interrogando i database della Flotta..."):
            # Inizializzazione rapida
            chiama_mcp("initialize", {"protocolVersion": "2026-01-01", "registration_code": REG_CODE})
            chiama_mcp("notifications/initialized", {})
            
            # Tentativo di registrazione
            res = chiama_mcp("tools/call", {
                "name": "register",
                "arguments": {
                    "username": nuovo_username,
                    "empire": "crimson",
                    "registration_code": REG_CODE
                }
            })
            
            # Analisi intelligente della risposta
            if "result" in res:
                content = res["result"].get("content", [])
                text_response = content[0].get("text", "") if content else ""
                
                if "Error: username_taken" in text_response:
                    st.error(f"❌ Anche '{nuovo_username}' è già occupato! Prova con qualcosa di più originale.")
                elif "session_id" in text_response:
                    # Estraiamo il session_id dal testo (il server lo manda spesso in formato stringa)
                    # Cerchiamo di trovare la parte dopo 'session_id=' o simile
                    try:
                        # Se il server risponde con un JSON nel testo, lo carichiamo
                        import re
                        match = re.search(r'session_id=([a-zA-Z0-9\-_]+)', text_response)
                        if match:
                            st.session_state.session_id = match.group(1)
                            st.success("✅ Identità confermata! Benvenuto a bordo.")
                            st.rerun()
                        else:
                            st.warning("Il server ha risposto ma il Session ID è criptato. Controlla il log sotto.")
                            st.json(res)
                    except:
                        st.json(res)
                else:
                    st.info("Risposta ricevuta dal server:")
                    st.write(text_response)
            else:
                st.error("Errore di connessione.")
                st.json(res)

else:
    st.success("📡 SESSIONE ATTIVA")
    if st.button("📡 SCANSIONE SETTORE"):
        res = chiama_mcp("tools/call", {
            "name": "scan_sector",
            "arguments": {"session_id": st.session_state.session_id}
        })
        st.json(res)
