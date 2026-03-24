import streamlit as st
import requests
import time

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="Crimson Fleet: Tool Access", page_icon="🏴‍☠️")

REG_CODE = "8b4586fc4c72d5814472c5f35a93c235"
API_URL = "https://game.spacemolt.com/mcp"

st.markdown("""
    <style>
    .main { background-color: #0a0000; color: #ff3333; font-family: 'Courier New'; }
    .stButton>button { width: 100%; border: 1px solid #ff3333; background-color: #300; color: #f33; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

def invia_mcp(metodo, params):
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

# --- LOGICA DI REGISTRAZIONE ---
if 'session_id' not in st.session_state:
    st.session_state.session_id = None

st.title("🏴‍☠️ SpaceMolt: Hub Operativo")

if not st.session_state.session_id:
    st.subheader("⚔️ Reclutamento Crimson Fleet")
    # Generiamo un nome unico per evitare l'errore 'username_taken'
    temp_name = f"Corsaro_{int(time.time()) % 1000}"
    user_name = st.text_input("Inserisci il tuo nome pirata", temp_name)
    
    if st.button("🔴 AVVIA REGISTRAZIONE STRUMENTALE"):
        with st.spinner("Sincronizzazione Handshake..."):
            # 1. Handshake Iniziale (Necessario per ogni sessione)
            invia_mcp("initialize", {
                "protocolVersion": "2026-01-01", 
                "registration_code": REG_CODE
            })
            invia_mcp("notifications/initialized", {})
            
            # 2. CHIAMATA AL TOOL (Ecco la correzione!)
            # register non è un metodo, è un TOOL chiamato via tools/call
            res = invia_mcp("tools/call", {
                "name": "register",
                "arguments": {
                    "username": user_name,
                    "empire": "crimson",
                    "registration_code": REG_CODE
                }
            })
            
            st.write("📂 **Analisi Risposta:**")
            if "result" in res:
                # Il server risponde con una lista in 'content'
                content = res["result"].get("content", [])
                text_out = content[0].get("text", "") if content else ""
                
                # Cerchiamo il Session ID nella risposta testuale
                if "session_id" in text_out.lower() or "session_id" in str(res):
                    # Cerchiamo di estrarre il token (spesso è una stringa lunga)
                    import re
                    match = re.search(r'session_id[\"\'\s:=]+([a-zA-Z0-9\-_]+)', str(res))
                    if match:
                        st.session_state.session_id = match.group(1)
                        st.success(f"✅ Benvenuto, Capitano {user_name}! Sessione sbloccata.")
                        st.rerun()
                    else:
                        st.warning("Il server ha risposto ma l'ID è nascosto. Controlla il JSON sotto.")
                        st.json(res)
                else:
                    st.error("Il server ha rifiutato la registrazione. Leggi il messaggio:")
                    st.json(res)
            else:
                st.error("Errore di protocollo.")
                st.json(res)
else:
    st.success(f"📡 COLLEGATO: Sessione `{st.session_state.session_id[:12]}...`")
    
    if st.button("📡 SCANSIONE RADAR"):
        # Anche la scansione è un TOOL
        scan = invia_mcp("tools/call", {
            "name": "scan_sector",
            "arguments": {"session_id": st.session_state.session_id}
        })
        st.json(scan)

    if st.button("🔴 RESET SESSIONE"):
        st.session_state.session_id = None
        st.rerun()
