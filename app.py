import streamlit as st
import asyncio
import httpx
from mcp import ClientSession
from mcp.client.sse import sse_client
import time
import traceback

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="Crimson Fleet: MCP Link", page_icon="🏴‍☠️")
REG_CODE = "8b4586fc4c72d5814472c5f35a93c235"
MCP_URL = "https://game.spacemolt.com/mcp"

st.markdown("<style>.main { background-color: #0a0505; color: #ff3333; font-family: monospace; }</style>", unsafe_allow_html=True)

# --- MOTORE MCP AVANZATO ---
async def chiama_mcp_robust(tool_name, arguments={}):
    """Apre il tunnel, esegue il comando e gestisce le eccezioni annidate"""
    try:
        # Aumentiamo il timeout per le connessioni mobili Android
        timeout = httpx.Timeout(20.0, connect=10.0)
        
        async with sse_client(MCP_URL, timeout=timeout) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                # Inizializzazione con timeout
                await asyncio.wait_for(session.initialize(), timeout=10.0)
                
                # Prepariamo gli argomenti con la chiave richiesta dal server
                full_args = {**arguments, "registration_code": REG_CODE}
                
                # Esecuzione Tool
                result = await session.call_tool(tool_name, full_args)
                return result.content, "SUCCESS"
                
    except asyncio.TimeoutError:
        return None, "TIMEOUT: Il server SpaceMolt non ha risposto in tempo."
    except Exception as e:
        # Qui "spacchettiamo" la TaskGroup per l'utente
        error_details = traceback.format_exc()
        if "HTTPStatusError" in error_details:
            return None, f"ERRORE HTTP: Il server ha rifiutato la connessione (probabile 404 o 500)."
        return None, f"DETTAGLIO ERRORE: {str(e)}"

# --- INTERFACCIA ---
st.title("🏴‍☠️ Crimson Fleet: MCP Link")

if 'session_id' not in st.session_state:
    st.session_state.session_id = None

if not st.session_state.session_id:
    st.subheader("⚔️ Reclutamento Nucleare")
    captain_name = st.text_input("Nome Pirata", f"Kaelen_Rex_{int(time.time())%1000}")
    
    if st.button("🔴 REGISTRA VIA MCP"):
        with st.spinner("Forzatura tunnel MCP..."):
            # Gestione sicura del loop asincrono in Streamlit
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                response, status = loop.run_until_complete(chiama_mcp_robust("register", {
                    "username": captain_name,
                    "empire": "crimson"
                }))
                
                if response:
                    res_str = str(response)
                    if "session_id" in res_str:
                        import re
                        match = re.search(r'session_id[\"\'\s:=]+([a-zA-Z0-9\-_]+)', res_str)
                        if match:
                            st.session_state.session_id = match.group(1)
                            st.session_state.captain = captain_name
                            st.success(f"Benvenuto Capitano {captain_name}!")
                            st.rerun()
                    st.write("📂 **Risposta Server:**")
                    st.write(response)
                else:
                    st.error(status)
            except Exception as e:
                st.error(f"Errore critico del loop: {e}")
            finally:
                loop.close()

else:
    st.success(f"📡 COLLEGATO: {st.session_state.captain}")
    if st.button("📡 SCANSIONE SETTORE"):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        res, status = loop.run_until_complete(chiama_mcp_robust("scan_sector", {
            "session_id": st.session_state.session_id
        }))
        st.json(res if res else status)
        loop.close()
