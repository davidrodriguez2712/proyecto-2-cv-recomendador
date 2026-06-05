import streamlit as st
import sys
from pathlib import Path

PARENT_DIR = Path.cwd().parent
sys.path.append(f'{PARENT_DIR}/proyect1/ui')


st.set_page_config(
    page_title= "APP CV Reclutador",
    page_icon= "💼"
)

if "token" not in st.session_state:
    st.session_state.token = None

print(st.session_state.token)

if st.session_state.token is None:
    print(st.session_state.token == None)
    st.switch_page("pages/Login.py")
    
else:
    st.switch_page("pages/Chat.py")

