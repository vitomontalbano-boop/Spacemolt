import streamlit as st
import requests
import time

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="Crimson Fleet: Deep Scan", page_icon="🏴‍☠️")

REG_CODE = "8b4586fc4c72d5814472c5f35a93c235"
API_URL = "https://game.spacemolt.com/mcp"

st.markdown("""
    <style>
    .main { background-color: #050000; color: #ff0000; font-family: 'Courier New'; }
    .stButton>button { width: 100%; border: 1px solid #ff0000; background-color: #200; color: #f00; height: 3em; }
    .debug-box { background-color: #111; border: 1px solid #444; padding: 10px; color: #aaa; font-size: 0.8em; }
    </style>
    """, unsafe_allow_html=True)

def chiama_mcp_sicuro(metodo, params):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {REG_CODE}",
        "User-Agent": "Mozilla/5.0 (Android)" # Simuliamo un browser mobile
    }
    payload = {"jsonrpc": "2.0", "method": metodo, "params": params, "id": int(time.time())}
    
    try:
        r = requests.post(API_URL, json=payload, headers=headers, timeout=15)
        
        # Se il server risponde correttamente (200 OK)
        if r.status_code == 200:
            try:
                return r.json(), "OK"
            except:
                return None, f"Errore: Il server ha risposto con testo semplice: {r.text[:200]}"
        else:
            return None, f"Errore Server: Codice Stato {r.status_code}. Risposta: {r.text[:200]}"
            
    except Exception as e:
        return None, f"Errore di Rete: {str(e)}"

# --- INTERFACCIA ---
st.title("🏴‍☠️ Terminale di Emergenza")
st.write("⚓️ *Il segnale è instabile. Tentativo di aggancio forzato.*")

if 'session_id' not in st.session_state:
    st.session_state.session_id = None

if not st.session_state.session_id:
    # Prova un nome molto strano per evitare il 'username_taken'
    default_name = f"Pirata_{int(time.time()) % 10000}"
    user_name = st.text_input("Scegli un nome unico (es: Shadow_Bucaneer_7)", default_name)
    
    if st.button("🔴 TENTA REGISTRAZIONE DI EMERGENZA"):
        with st.spinner("Forzatura handshake..."):
            # 1. Inizializzazione rapida
            chiama_mcp_sicuro("initialize", {"protocolVersion": "2026-01-01", "registration_code": REG_CODE})
            chiama_mcp_sicuro("notifications/initialized", {})
            
            # 2. Registrazione
            res, status = chiama_mcp_sicuro("register", {
                "username": user_name,
                "empire": "crimson",
                "registration_code": REG_CODE
            })
            
            if res:
                st.write("📂 **Risposta Ricevuta:**")
                st.json(res)
                # Logica per estrarre session_id come prima...
            else:
                st.error(status)
                st.info("💡 Suggerimento: Se vedi 'Status 403' o '404', il server SpaceMolt potrebbe aver bloccato l'IP di Streamlit.")
else:
    st.success("📡 SESSIONE ATTIVA")
    if st.button("📡 SCANSIONE"):
        res, status = chiama_mcp_sicuro("tools/call", {
            "name": "scan_sector",
            "arguments": {"session_id": st.session_state.session_id}
        })
        st.json(res if res else status)

if st.button("🧹 Pulisci Log"):
    st.rerun()
