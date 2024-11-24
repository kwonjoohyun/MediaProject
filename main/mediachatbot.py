import streamlit as st
from dotenv import load_dotenv
from llm import get_ai_response 


st.set_page_config(
    page_title="아주대학교 미디어학과 ChatBot",
    page_icon=r"C:\Users\권주현\Desktop\dataset\media.png",
    layout="centered"
)


st.title("Chat MEDIA")
st.caption("아주대학교 미디어학과와 관련된 것을 답해드립니다!")


load_dotenv()


if 'message_list' not in st.session_state:
    st.session_state.message_list = []


def display_message(role, content):
    alignment = "flex-end" if role == "user" else "flex-start"
    bg_color = "#EDEDED" if role == "user" else "#EDEDED"
    st.markdown(
        f"""
        <div style="
            display: flex;
            justify-content: {alignment};
            margin-bottom: 10px;
        ">
            <div style="
                background-color: {bg_color};
                padding: 10px 15px;
                border-radius: 15px;
                max-width: 70%;
                word-wrap: break-word;
            ">
                {content}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


for message in st.session_state.message_list:
    display_message(message["role"], message["content"])


if user_question := st.chat_input(placeholder="미디어학과에 관련된 궁금한 내용들을 말씀해주세요!"):
    display_message("user", user_question)
    st.session_state.message_list.append({"role": "user", "content": user_question})

    
    with st.spinner("답변을 생성하는 중입니다..."):
        ai_response = get_ai_response(user_question)
        print(f"AI Response: {ai_response}") 
        display_message("ai", ai_response)
        st.session_state.message_list.append({"role": "ai", "content": ai_response})
