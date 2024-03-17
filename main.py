from functions import *

"""
Simple vocal assistant using speech recognition and GPT api.

1) Put your openAI API key in the file /OpenAI_Key.txt
2) Customize your key words and languages below
3) Start talking with your assisstant

API management: https://platform.openai.com/usage
Sounds library: https://pixabay.com/sound-effects/search/notification/
Offline GPT: https://theresanaiforthat.com/ai/offline-chatgpt/
"""

"""
PARAMETERS/CUSTOMIZATION
"""

#conversation
messages = [{"role": "user", "content": "Make complete but short answers without echoing responses."}] #put initial instructions here.
start_keywords = ["Windows","windows"] #words that will awake the assistant and start the listening (better if the word is easily recognized)
end_keywords = ["merci", "Merci", "Thank", "thank"] #words or words parts that will stop the conversation with the assisstant and the listening (better if the word is easily recognized)
speech_correction = True #activate if you want gpt to correct or interpret your speech in a specific way
instructions = "give me the corrected text for this sentence considering it can be part of a conversation: " #instructions for speech correction

#models
gpt_model="gpt-3.5-turbo-1106" #chat gpt model to use
speech_language='en-US' #fr-FR #language to recognize and understand #check this for supported languages: https://cloud.google.com/speech-to-text/docs/speech-to-text-supported-languages
answer_language='english' #this will be given to chat gpt, put the wanted language name, you can put "" to let chat gpt decide.

"""
MAIN CODE
"""

try_again=False
text = ""
active_answer = False
end_answer = False

while True:
    if not try_again: #listen and wait for a start keyword
        text = record_text(speech_language,active_answer)
        print("\n\nUSER: "+text)

    try:
        #check if start word in raw text
        if not active_answer:
            active_answer,pos,word = check_text(text,start_keywords)
            if(pos>=0):
                text = text[pos+len(word):] #interpret text from keyword position
                print("Text Considered: " + text)
                play_sound("start_sound.wav") #start of the conversation
            else:
                print("No start key words found...pass\n")

        #the assistant answers if we are talking to it
        if active_answer:
            corrected_text = text
            if speech_correction:
                corrected_text = timeout_handler(correct_with_gpt, (text,gpt_model,instructions), timeout=3)
            print("corrected text: " + corrected_text)
            corrected_text = filter_text(corrected_text,corrected_text)
            print("final understood text: " + corrected_text)
            # check if end word in corrected
            if not end_answer:
                end_answer, pos, word = check_text(corrected_text, end_keywords)
                if (pos >= 0):
                    corrected_text = corrected_text[:pos] + word
                    print("final considered text: " + corrected_text)

            try:
                if answer_language != "":
                    messages.append({"role": "user", "content": corrected_text + "(answer me in "+answer_language+")"})
                response = timeout_handler(send_to_chatGPT, (messages,gpt_model,), timeout=3)
                print("\nAssistant: " + response+"\n")
                SpeakText(response)
                try_again = False
                if end_answer:
                    active_answer = False
                    end_answer = False
                    play_sound("end_sound.wav")  # end of the conversation

            except Exception as error:
                print("\nNo answer from GPT...trying again")
                try_again = True
                print(error)
    except Exception as error:
        print("\nNo correction from GPT...trying again")
        print(error)
        try_again = True
