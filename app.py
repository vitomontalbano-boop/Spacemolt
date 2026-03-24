import streamlit as st
import requests
import time

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="Crimson Fleet: Kaelen-1", page_icon="🏴‍☠️")
REG_CODE = "8b4586fc4c72d5814472c5f35a93c235"
API_URL = "https://game.spacemolt.com/mcp"

# Estetica Pirata
st.markdown("<style>.main { background-color: #100; color: #f33; font-family: monospace; }</style>", unsafe_allow_html=True)

def chiama_spacemolt(metodo, params):
    """Il cuore del protocollo MCP: invia richieste JSON-RPC"""
    payload = {
        "jsonrpc": "2.0",
        "method": metodo,
        "params": {**params, "registration_code": REG_CODE},
        "id": int(time.time())
    }
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {REG_CODE}"}
    try:
        r = requests.post(API_URL, json=payload, headers=headers, timeout=15)
        return r.json()
    except Exception as e:
        return {"error": str(e)}

# --- STATO DELLA NAVE ---
if 'session_id' not in st.session_state:
    st.session_state.session_id = None
if 'username' not in st.session_state:
    st.session_state.username = ""

st.title("🏴‍☠️ SpaceMolt: Terminale Kaelen")

if not st.session_state.session_id:
    st.subheader("⚔️ Reclutamento Crimson Fleet")
    # Usiamo un nome pirata unico per evitare l'errore 'username_taken'
    suggerimento = f"Kaelen_Crimson_{int(time.time()) % 1000}"
    user_name = st.text_input("Scegli il tuo nome da battaglia", suggerimento)
    
    if st.button("🔴 GIURA FEDELTÀ ALLA FLOTTA"):
        with st.spinner("Sincronizzazione neurale..."):
            # 1. Inizializzazione (Sempre richiesta)
            chiama_spacemolt("initialize", {"protocolVersion": "2026-01-01"})
            chiama_spacemolt("notifications/initialized", {})
            
            # 2. Registrazione (Tentativo come metodo DIRETTO, non come tool)
            res = chiama_spacemolt("register", {
                "username": user_name,
                "empire": "crimson"
            })
            
            # Controllo se la risposta contiene il session_id (anche se annidato)
            res_str = str(res)
            if "session_id" in res_str:
                # Estrazione rozza ma efficace del session_id
                import re
                match = re.search(r'session_id[\"\'\s:=]+([a-zA-Z0-9\-_]+)', res_str)
                if match:
                    st.session_state.session_id = match.group(1)
                    st.session_state.username = user_name
                    st.success(f"Benvenuto, Capitano {user_name}!")
                    st.rerun()
            
            st.error("Il server non ha rilasciato l'ID. Debug:")
            st.json(res)

else:
    # --- PANNELLO OPERATIVO ---
    st.success(f"📡 COLLEGATO: {st.session_state.username}")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📡 SCANSIONE"):
            # Nota: il server vuole session_id dentro i params
            res = chiama_spacemolt("tools/call", {
                "name": "scan_sector", 
                "arguments": {"session_id": st.session_state.session_id}
            })
            st.json(res)
            
    with col2:
        if st.button("🛡️ STATO"):
            res = chiama_spacemolt("tools/call", {
                "name": "get_status", 
                "arguments": {"session_id": st.session_state.session_id}
            })
            st.json(res)

    if st.button("🔴 LOGOUT"):
        st.session_state.session_id = None
        st.rerun()
