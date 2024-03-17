import speech_recognition as sr
from dotenv import load_dotenv
from openai import OpenAI
import pyttsx3
import threading
import pygame
import time

load_dotenv()

#Chat gpt connection
client = OpenAI(
    api_key = (open('OpenAI_Key.txt').readlines())[0],
    )

#speech recognition
r = sr.Recognizer()

def play_sound(file_path):
    pygame.init()
    pygame.mixer.init()

    try:
        sound = pygame.mixer.Sound(file_path)
        sound.set_volume(1.0)  # Set the volume level (0.0 to 1.0)
        sound.play()
        time.sleep(sound.get_length())  # Wait for the sound to finish playing
    except pygame.error as e:
        print(f"Error playing sound: {e}")
    finally:
        pygame.quit()

def timeout_handler(func, args, timeout):
    result = None

    def worker():
        nonlocal result
        result = func(*args)

    thread = threading.Thread(target=worker)
    thread.start()
    thread.join(timeout)

    if thread.is_alive():
        thread._stop()  # Forcefully stop the thread if it's still running
        raise TimeoutError("Function call timed out")

    return result

def SpeakText(command):
    """
    https://pyttsx3.readthedocs.io/en/latest/engine.html
    """
    engine = pyttsx3.init()
    """RATE"""
    engine.setProperty('rate', 180)  # setting up new voice rate
    """VOICE"""
    voices = engine.getProperty('voices')  # getting details of current voice
    engine.setProperty('voice', voices[1].id)  # changing index, changes voices. 1 for female

    engine.say(command)
    engine.runAndWait()

def record_text(language_code,active_answer):
    t0 = time.time()
    while True:
        try:
            with sr.Microphone() as source2:
                r.adjust_for_ambient_noise(source2, duration=0.5)
                print("\rListening...",end="")
                audio2 = r.listen(source2)
                print("Analysing...", end="")
                MyText = r.recognize_google(audio2, language=language_code)
                return MyText
        except sr.RequestError as e:
            print("Could not request results: {0}".format(e))
        except sr.UnknownValueError:
            pass
            #print("Unknown error")"""

        # play sounds continiously if conversation ongoing
        if active_answer and time.time()-t0 > 5:
            play_sound("conv_sound.mp3")
            t0 = time.time()

def send_to_chatGPT(messages, model):
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        max_tokens=1000,
        n=1,
        stop=None,
        temperature=0.5,
    )
    message = response.choices[0].message.content
    messages.append(response.choices[0].message)
    return message

def correct_with_gpt(message, model, instructions):
    conv = []
    conv.append({"role": "user", "content": instructions+message})
    response = client.chat.completions.create(
        model=model,
        messages=conv,
        max_tokens=1000,
        n=1,
        stop=None,
        temperature=0.2, #high = more creativity and may be less coherence, low = more coherence, less creativity
    )
    message = response.choices[0].message.content
    return message

def check_text(key_text,key_words_list):
    pos = -1
    word = ""
    for key_word in key_words_list:
        try:
            pos = key_text.index(key_word)
            word = key_word
        except:
            pass

    if pos != -1:
        return True,pos,word
    else:
        return False,-1,word

def filter_text(text_to_filter,corrected_text):
    key_list = ['->','- "'] #allow to clean specific cases
    for key in key_list:
        try:
            new_text_pos = text_to_filter.index(key)
            return text_to_filter[new_text_pos+2:]
        except:
            pass
    return text_to_filter