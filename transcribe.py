import os

from openai import OpenAI

def trans():

    api_key = "Your API Key"  # Replace with your actual API key
    client = OpenAI(api_key=api_key)
    restext = ""
    with open("output.wav", "rb") as audio_file:
            transcription = client.audio.transcriptions.create(
                model="whisper-1", 
                file=audio_file,
                language="en"  # Specify the language as English
            )
            restext = transcription.text
            print(restext)
    try:
            os.remove("output.wav")
            print("Success", "File deleted successfully!")
    except FileNotFoundError:
            print("Warning", "The file does not exist.")
    except Exception as e:
            print("Error", f"An error occurred: {e}")
    return(restext)
    
