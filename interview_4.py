import streamlit as st
import speech_recognition as sr
import io
from audio_recorder_streamlit import audio_recorder
import pyttsx3
import os
import json
from ai21 import AI21Client
from ai21.models.chat import ChatMessage

os.environ["AI21_API_KEY"] = "AdWkhSmvVEMbaTSc7MqfMG5rBveZPSoN"

client = AI21Client(api_key=os.getenv("AI21_API_KEY"))

def handle_conversation(messages, model="jamba-instruct-preview", n=1, max_tokens=1024, temperature=0.7, top_p=1, stop=[]):
  
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        n=n,
        max_tokens=max_tokens,
        temperature=temperature,
        top_p=top_p,
        stop=stop,
    )
    
   
    if response.choices:
        return response.choices[0].message.content
    else:
        return None


questions = [
    "What is your name?",
    "Tell me about yourself.",
    "Why do you want this job?",
    "What are your strengths and weaknesses?"
]


recognizer = sr.Recognizer()


def ask_question_once():
    if not st.session_state.get('question_asked'):
        engine = pyttsx3.init()
        question = questions[st.session_state.question_index]
        engine.say(question)
        engine.runAndWait()
        st.session_state.question_asked = True  


def interview():
    if 'question_index' not in st.session_state:
        st.session_state.question_index = 0
        st.session_state.answers = []
        st.session_state.question_asked = False  
    
   
    ask_question_once()

  
    question = questions[st.session_state.question_index]
    st.write(f"Question: {question}")

    
    audio_bytes = audio_recorder()

    if audio_bytes:
        
        st.audio(audio_bytes, format="audio/wav")

    
        wav_file = io.BytesIO(audio_bytes)
        with sr.AudioFile(wav_file) as source:
            audio_data = recognizer.record(source)
            try:
                text = recognizer.recognize_google(audio_data)
                st.write(f"Transcribed Text: {text}")
                
            
                if st.button("Submit Answer", key=f"submit_answer_{st.session_state.question_index}"):  
                   
                    st.session_state.answers.append(text)
                    st.session_state.question_asked = False 
                    if st.session_state.question_index < len(questions) - 1:
                        st.session_state.question_index += 1
                    else:
                        st.session_state.page = "finish"
                    st.rerun()
            except sr.UnknownValueError:
                st.write("Could not understand audio.")
            except sr.RequestError:
                st.write("Speech Recognition service error.")


def finish_page():
    st.title("Interview Finished!")
    
    st.write("Thank you for completing the interview.")
    

    for i, answer in enumerate(st.session_state.answers):
        st.write(f"Question {i + 1}: {questions[i]}")
        st.write(f"Answer: {answer}")
    

    if st.button("Submit and Analyze", key="submit_analyze"):  
  
        st.session_state.page = "analysis"
        st.rerun()


def analysis_page():
    st.title("Interview Analysis")
    
    interview_data = ""
    for i, (question, answer) in enumerate(zip(questions, st.session_state.answers), start=1):
        interview_data += f"{i}. **Question:** {question}\n"
        interview_data += f"   - **Answer:** {answer}\n\n"

    messages = [
        ChatMessage(
            content=f"""
You are a HR Manager conducting an interview and is rating the candidate based on following parameters.
The analysis should be done from a hiring point of view. Very Short answers are not encouraged.
Be strict and do not give any parameter more than 90.
Based on the candidate's written answers to the following questions, 
evaluate their responses using the parameters below. 
Rate each parameter from 1 to 100, where 1 is the lowest and 100 is the highest. 

The questions and answers are as follows:
{interview_data}
Give honest replies and evaluate it correctly.
Please evaluate the candidate’s performance on the following parameters:
1. **Clarity and Conciseness**
2. **Grammar and Structure**
3. **Relevance**
4. **Confidence**
5. **Communication Skills**
6. **Emotional Tone and Sentiment**
7. **Answer Length**: The answer should be not short.
8. **Important Points (Impression Points)**: Identify key strengths or weaknesses in the answers. What are the most important points the candidate emphasizes? These could include knowledge, professionalism, or personality traits that stood out.

Please provide your analysis in the following HTML format, with numerical values between 1 and 100 for each parameter, and include a three important points under `"imp_points"`for advise on improving. Do not provide extra information:

<div>
    <h3>Evaluation Report</h3>
    <ul>
        <li><strong>Clarity & Conciseness:</strong> number </li>
        <li><strong>Grammar & Structure:</strong> number</li>
        <li><strong>Relevance:</strong> number</li>
        <li><strong>Confidence:</strong> number</li>
        <li><strong>Communication Skills:</strong> number</li>
        <li><strong>Emotional Tone & Sentiment:</strong> number</li>
        <li><strong>Answer Length:</strong> number</li>
    </ul>
    <h4>Important Points for Improvement:</h4>
    <ul>
        <li>imp_points</li>
    </ul>
</div>

""", role="assistant"
        )
    ]
    ai_response = handle_conversation(messages, model="jamba-instruct-preview", n=1, max_tokens=1024, temperature=0.7, top_p=1, stop=[])
    st.markdown(ai_response, unsafe_allow_html=True)


    if st.button("Go to Homepage", key="go_Interviewpage"):  
  
        st.session_state.page = "Interviewpage"
        st.session_state.question_index = 0
        st.session_state.answers = []
        st.session_state.question_asked = False
        st.rerun()


