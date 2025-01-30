import streamlit as st
from learning_path import LearningPlanApp
from interview_4 import interview, ask_question_once, finish_page, analysis_page
from course_recommender import CourseRecommender
from master import Chatbot, initialize_chat
import pathlib

hide_streamlit_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
.stDeployButton {display:none;}
</style>

"""


def load_css(file_path):
    with open(file_path) as f:
        st.markdown(f"<style>{f.read()}</stlye>",unsafe_allow_html=True)

css_path = pathlib.Path("style.css")
load_css(css_path)
st.markdown(hide_streamlit_style, unsafe_allow_html=True) 

with st.sidebar:
    st.title("MasterAI")
    page = st.radio("Choose a feature:", ["Home", "AI Chat", "Course Recommender", "Learning Path", "Interview Simulator"])

if page == "Home":
    
    st.header("Welcome to MasterAI!")
    st.write("Explore AI-powered features to enhance your learning and career growth.")
    st.markdown("""
MasterAI is an AI-powered learning platform that offers personalized course recommendations, 
real-time feedback, and adaptive learning paths. Using advanced machine learning and NLP, 
it helps users optimize their learning experience, track progress, 
and prepare for real-world challenges like job interviews with interactive AI simulations.""")

elif page == "AI Chat":
    ai21_api_key = "AdWkhSmvVEMbaTSc7MqfMG5rBveZPSoN"
    playht_user_id = "mK6xsWRBTyOAKXbAHHBDvW6EvzE2"
    playht_api_key = "f0bc7cef391640b1b0be4fd6a6163779"
    chatbot = Chatbot(ai21_api_key, playht_user_id, playht_api_key)

   
    st.title("Choose your chatbot and start your journey...")

   
    if "openai_model" not in st.session_state:
        st.session_state["openai_model"] = "jamba-instruct-preview"

    if "messages" not in st.session_state:
        st.session_state.messages = []

  
    col1, col2 = st.columns(2)
    with col1:
        if st.button("MasterAI", key="masterai"):
            st.session_state.messages = initialize_chat("MasterAI")
    with col2:
        if st.button("ComicBot", key="comic"):
            st.session_state.messages = initialize_chat("ComicBot")

    for message in st.session_state.messages:
        if message["role"] != "system":
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    if prompt := st.chat_input("What is up?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            ai_content = chatbot.get_ai21_response(st.session_state.messages)
            st.markdown(ai_content)

            audio_file = chatbot.text_to_speech(ai_content)
            st.audio(audio_file, format="audio/wav")

            st.session_state.messages.append({"role": "assistant", "content": ai_content, "audio_file": audio_file})

        

elif page == "Course Recommender":
    st.header("Course Recommender")
    recommender = CourseRecommender(data_path='courses (1).csv')
    recommender.run_streamlit_app()

elif page == "Learning Path":

    app = LearningPlanApp()
    app.run()


elif page == "Interview Simulator":
    st.header("AI Interview Simulator")
    questions = [
    "What is your name?",
    "Tell me about yourself.",
    "What are your strengths and weaknesses?"
    ]
    if 'page' not in st.session_state:
        st.session_state.page = "Interviewpage"

    if st.session_state.page == "Interviewpage":
     
        if st.button("Start Interview", key="start_interview_page"):  
            st.session_state.page = "interview"
            st.rerun()
    elif st.session_state.page == "interview":
        interview()
    elif st.session_state.page == "finish":
        finish_page()
    elif st.session_state.page == "analysis":
        analysis_page()