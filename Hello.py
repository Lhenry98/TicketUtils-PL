import streamlit as st

st.set_page_config(page_title="Welcome")

hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            .css-1rs6os {visibility: hidden;}
            .css-17ziqus {visibility: hidden;}
            """
st.markdown(hide_st_style,unsafe_allow_html=True)
            
st.write("# Welcome! 👋")

st.markdown("##")

name = st.text_input('Password')

if 'key' not in st.session_state:
    st.session_state.key = 0

if name == st.secrets["soldout"]["soldout"]:
    st.session_state.key = 1
elif name == st.secrets["moody"]["moody"]:
    st.session_state.key = 2
elif name == st.secrets["zilker"]["zilker"]:
    st.session_state.key = 3
elif name == st.secrets["cfg"]["cfg"]:
    st.session_state.key = 4
else:
    st.session_state.key = 0
#-------------------------------------
if st.session_state.key == 1:
    st.write('Success, you are free to browse!')
elif st.session_state.key == 2:
    st.write('Success, you are free to browse!')
elif st.session_state.key == 3:
    st.write('Success, you are free to browse!')
elif st.session_state.key == 4:
    st.write('Success, you are free to browse!')
else:
    st.write("Input your password and press [ENTER]")
