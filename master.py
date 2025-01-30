
from ai21 import AI21Client
from ai21.models.chat import ChatMessage
import pygame
from pyht import Client
from pyht.client import TTSOptions
import os

class Chatbot:
    def __init__(self, ai21_api_key, playht_user_id, playht_api_key):
        self.ai21_client = AI21Client(api_key=ai21_api_key)
        self.playht_client = Client(user_id=playht_user_id, api_key=playht_api_key)
        pygame.mixer.init()

    def text_to_speech(self, text):
        options = TTSOptions(voice="s3://voice-cloning-zero-shot/19eb3e14-53c4-432b-a56f-04561d6540b7/original/manifest.json")
        filename = "output.wav"
        with open(filename, "wb") as f:
            for chunk in self.playht_client.tts(text, options, voice_engine='PlayDialog-http'):
                f.write(chunk)
        return filename

    def get_ai21_response(self, messages, model="jamba-instruct-preview", max_tokens=200, temperature=0.7, top_p=1):
        ai21_messages = [ChatMessage(role=m["role"], content=m["content"]) for m in messages]
        response = self.ai21_client.chat.completions.create(
            model=model,
            messages=ai21_messages,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
            stop=[]
        )
        if response.choices:
            return response.choices[0].message.content
        return "Interruption..."


character_prompts = {
    "MasterAI": "You are a friendly chatbot. Your name is MasterAI. You are a teacher who teaches students in a very simple manner without any complicated words, using real-life examples.",
    "ComicBot": "You are a humorous chatbot. Your name is ComicBot. You love to tell jokes and make people laugh while providing helpful information."
}

def initialize_chat(character):
    return [{"role": "system", "content": character_prompts[character]}]