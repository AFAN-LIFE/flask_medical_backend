import time
import warnings
import streamlit as st
from llm.qianfan import get_polish_response

def stream_return(string, interval=0.01):
    for word in string:
        yield word['result']
        time.sleep(interval)
def llm_dialog_show(content, prompt):
    @st.dialog('AI小逸', width='large')
    def llm_response(content, prompt):
        result = get_polish_response(content, prompt)
        st.write_stream(stream_return(result))

    def llm_button_view(content, prompt):
        if st.button('试试让AI小逸分析结果吧！'):
            llm_response(content, prompt)

    llm_button_view(content, prompt)

def llm_expander_show(content, prompt):
    def llm_response(content, prompt):
        result = get_polish_response(content, prompt)
        st.write_stream(stream_return(result))

    with st.expander('试试让AI小逸分析结果吧！'):
        llm_response(content, prompt)
