import tkinter as tk
from tkinter import ttk, filedialog
from threading import Thread, Event
import pyaudio
import wave
import os
import json
from PIL import Image, ImageTk
import transcribe
from openai import OpenAI
import sys

api_key = "Your API Key"  # Replace with your actual API key
client = OpenAI(api_key=api_key)

class TabooApp:


    def __init__(self, master):
        
        self.master = master
        self.master.title("Let's Play Taboo Game!")
        self.master.configure(bg='#ececec')
        json_file_path = 'data.json'
        self.data_list = self.read_data_from_json(json_file_path)

        
        self.display_index = 0  # Change this index as needed

        # Create a frame to hold the buttons and the table
        self.main_frame = tk.Frame(self.master, bg='#ececec', padx=10, pady=10)
        self.main_frame.pack(pady=20)

        # Create the navigation buttons with custom style
        self.style = ttk.Style()
        self.style.configure('Navigation.TButton', font=('TkDefaultFont', 20), height=60)

        self.prev_button = ttk.Button(self.main_frame, text="<<", command=self.prev_card, style='Navigation.TButton',width=1.5)
        self.next_button = ttk.Button(self.main_frame, text=">>", command=self.change_card, style='Navigation.TButton',width=1.5)
        
    
        # Place the buttons on the left and right of the table
        self.prev_button.grid(row=0, column=0, padx=5)
        self.next_button.grid(row=0, column=2, padx=5)

        # Create a frame to hold the table
        self.table_frame = tk.Frame(self.main_frame, bg='white', padx=10, pady=10)
        self.table_frame.grid(row=0, column=1, padx=5)

        # Create and populate the table
        self.create_table(self.display_index)

        self.image_start = Image.open("pic/rec.png").resize((50, 50))
        self.image_stop = Image.open("pic/stop.png").resize((50, 50))


         # Create initial image
        self.current_image = self.image_start
        self.photo = ImageTk.PhotoImage(self.current_image)
         # Create initial image
        self.current_image = self.image_start
        self.photo = ImageTk.PhotoImage(self.current_image)

        # Create a circular button
        self.button = tk.Button(master, image=self.photo, command=self.toggle_recording, bd=0, highlightthickness=0)
        self.button.image = self.photo  # Keep a reference to the image to prevent garbage collection

        # Pack the button in the center of the window
        self.button.pack(pady=20)

        # Initialize recording state
        self.is_recording = False

        # Create a label for displaying recording status
        self.label_text = tk.StringVar()
        self.label_text.set("  ")
        self.status_label = tk.Label(master, textvariable=self.label_text,background='#ececec')
        self.status_label.pack()

        self.speech_text = tk.StringVar()
        self.speech_text.set(" ")
        #self.speech_label = tk.Label(master, textvariable=self.speech_text, background='#ececec', wraplength=300, justify="center")
        self.speech_label = tk.Label(master, textvariable=self.speech_text, font=('TkDefaultFont', 24), justify="center")
       
        self.speech_label.pack()

        # Configure font for speech_label
       # self.speech_label.config(font=('TkDefaultFont', 20, fg='black')  # Example: font size 24, dark blue text
        self.speech_label.config(font=('TkDefaultFont', 20), fg='black')


        
    #
    

         # Create a Frame for other widgets
        main_frame = ttk.Frame(root)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Create a Canvas to display the image
        self.canvas = tk.Canvas(main_frame, width=350, height=250,background='#ececec')
        self.canvas.pack(side=tk.RIGHT, anchor=tk.SE, padx=10, pady=10)

        # Load and display the photo
        self.load_and_display_photo()


        # Add a label on the Canvas (right side)
            # Create answer
        self.answer_text = tk.StringVar()
        self.answer_text.set(" um ..")
        #self.answer_label = tk.Label(master, textvariable=self.answer_text)
        self.label_label = ttk.Label(self.canvas, textvariable=self.answer_text, background="#DCE3F2", foreground="darkblue")
        self.label_label['font'] = ('TkDefaultFont',28)
        #self.answer_label.pack()
        #label_text = "Hello, this is a label on the image!"
        #self.label = ttk.Label(self.canvas, text=label_text, background='#ececec')
        self.label_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)


        #image = Image.open("pic/rec.png")  # Replace with the path to your image
        #image = image.resize((50, 50))  # Adjust the size as needed
        #photo = ImageTk.PhotoImage(image)
        # Create a circular button
        #button = tk.Button(root, image=photo, command=self.start_recording, bd=0, highlightthickness=0)
        #button.image = photo  # Keep a reference to the image to prevent garbage collection

        # Pack the button in the center of the window
        #button.pack(pady=20)

        #self.start_button = ttk.Button(self.master, text="Start Recording", command=self.start_recording)
        #self.start_button.pack(pady=10)

        #self.stop_button = ttk.Button(self.master, text="Stop Recording", command=self.stop_recording, state=tk.DISABLED)
        #self.stop_button.pack(pady=10)

        self.wav_file_path = "output.wav"
        self.recording_thread = None
        self.frames = []
        self.stop_recording_event = Event()
   
    def read_data_from_json(self,json_file):
    
    # Initialize data_list
        data_list = []

        try:
            # Read data from JSON file
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Iterate over each card in the JSON data and create the data_list
            for card in data['cards']:
                keyword = card['keyword']
                taboo_words = card['taboo_words']
                explanation = card['explanation']

                # Append to data_list in the required format
                data_list.append([keyword] + taboo_words + [explanation])

            return data_list
        
        except FileNotFoundError:
            print(f"Error: File '{json_file}' not found.")
            return []
        except json.JSONDecodeError:
            print(f"Error: JSON decoding failed for file '{json_file}'.")
            return []
    
    def change_card(self):
        self.display_index = (self.display_index + 1) % len(self.data_list)
        self.create_table(self.display_index)

    def prev_card(self):
        self.display_index = (self.display_index - 1) % len(self.data_list)
        self.create_table(self.display_index)

    def askopenfilename(self, **kwargs):
        try:
            return filedialog.askopenfilename(**kwargs)
        except Exception as e:
            print(f"Error in askopenfilename: {e}")
            return ""
  
    def toggle_recording(self):
        if self.is_recording:
            self.stop_recording()
        else:
            self.start_recording()
    def update_button_image(self):
        # Update the button image
        self.photo = ImageTk.PhotoImage(self.current_image)
        self.button.config(image=self.photo)

    def start_recording(self):

        self.reset_program()
        self.recording_thread = Thread(target=self.record_audio)
        self.recording_thread.start()
        
        # Change the button image to stop.png
        self.current_image = self.image_stop
        self.update_button_image()
        self.is_recording = True
        # Update label text
        self.label_text.set("Recording...")
        self.speech_text.set("..")

    def stop_recording(self):


        self.stop_recording_event.set()  # Set the event to signal the recording thread to stop
        # Change the button image back to start.png
        self.current_image = self.image_start
        self.update_button_image()

        # Update recording state
        self.is_recording = False
        # Update label text
        self.label_text.set("  ")
        self.master.after(500, self.show_speech)
    def reset_program(self):
        self.delete_file()
        self.label_text.set(".")
        self.speech_text.set("..")
        self.answer_text.set("..Um..")

        # Your code to reset the program and parameters goes here
        # This could include resetting variables, clearing input fields, etc.

        # Print a message to indicate the reset (you can remove this in the final version)
        print("Program reset")
    def send_clue(self,clue):
        gpt_assistant_prompt= "You are a Taboo game guesser. You should try to guess the word from the given clue. Only give the word you think it is answer. Do not answer as a sentence or add something else that is not your answer."
        gpt_user_prompt = clue
        gpt_prompt = gpt_assistant_prompt, gpt_user_prompt
        #print(gpt_prompt)


        message=[{"role": "assistant", "content": gpt_assistant_prompt}, {"role": "user", "content": gpt_user_prompt}]
        temperature=0.2
        max_tokens=256
        frequency_penalty=0.0


        response = client.chat.completions.create(
            model="gpt-4",
            messages = message,
            temperature=temperature,
            max_tokens=max_tokens,
            frequency_penalty=frequency_penalty
        )
        res = response.choices[0].message.content
        #print(res)
        #print(type(res))
        self.answer_text.set(res)
        #self.delete_file()
        
    
    def show_speech(self):
        restext = transcribe.trans()
        self.speech_text.set(restext)

        self.send_clue(restext)
        self.master.after(5000, self.restart_program)


        '''with open("output.wav", "rb") as audio_file:
            transcription = client.audio.transcriptions.create(
                model="whisper-1", 
                file=audio_file
            )
            self.speech_text.set(transcription.text)
            restext = transcription.text
            self.send_clue(restext)

            self.master.after(5000, self.restart_program)
            #self.delete_file()'''
    def record_audio(self, sample_rate=44100, channels=1, chunk_size=1024, format_=pyaudio.paInt16):
       
        p = pyaudio.PyAudio()

        stream = p.open(format=format_,
                        channels=channels,
                        rate=sample_rate,
                        input=True,
                        frames_per_buffer=chunk_size)

        #print("Recording...")

        self.status_label.config(font=('TkDefaultFont', 16))  # Example: font size 16
        self.label_text.set("Recording your explanation...")

        while not self.stop_recording_event.is_set():
            data = stream.read(chunk_size)
            self.frames.append(data)


        stream.stop_stream()
        stream.close()
        p.terminate()

        # Save the recorded audio to a WAV file
        with wave.open(self.wav_file_path, 'wb') as wf:
            wf.setnchannels(channels)
            wf.setsampwidth(p.get_sample_size(format_))
            wf.setframerate(sample_rate)
            wf.writeframes(b''.join(self.frames))

        recorded_time = len(self.frames) / sample_rate
        #print(f"Actual recording duration: {recorded_time:.2f} seconds")
    
    def delete_file(self):
        try:
            os.remove("output.wav")
            print("Success", "File deleted successfully!")
        except FileNotFoundError:
            print("Warning", "The file does not exist.")
        except Exception as e:
            print("Error", f"An error occurred: {e}")
            
    def restart_program(self):
        # Destroy the current Tkinter window
        self.master.destroy()

        # Restart the Python script
        python = sys.executable
        os.execl(python, python, *sys.argv)
    def load_and_display_photo(self):
            # Load the image from file
            image_path = "pic/agent6.png"  # Replace with the actual path to your image
            ##image = Image.open(image_path)

            # Resize the image as needed
            ##image = image.resize((400, 300),Image.LANCZOS)

            # Convert the Image object to PhotoImage
            ##photo = ImageTk.PhotoImage(image)

            # Display the image on the Canvas
            ##self.canvas.create_image(0, 0, anchor=tk.NW, image=photo)
            ##self.canvas.photo = photo  # To prevent the image from being garbage collected  


            original_image = Image.open(image_path)

            # Calculate the aspect ratio to maintain the image proportions
            width, height = original_image.size
            aspect_ratio = width / height

            # Calculate the new dimensions to fit within the canvas
            canvas_width = 400
            canvas_height = int(canvas_width / aspect_ratio)

            # Resize the image
            resized_image = original_image.resize((canvas_width, canvas_height), Image.LANCZOS)

            # Convert the resized Image object to PhotoImage
            photo = ImageTk.PhotoImage(resized_image)

            # Display the image on the Canvas
            self.canvas.create_image(0, 0, anchor=tk.NW, image=photo)
            self.canvas.photo = photo  # To prevent the image from being garbage collected
    def count_images_in_folder(self,folder_path):
        image_extensions = ['.png', '.PNG']  # Add more extensions if needed
        image_count = 0

        try:
            # Get the list of files in the folder
            files = os.listdir(folder_path)
            print(files)

            # Count the image files
            for file in files:
                _, extension = os.path.splitext(file.lower())
                if extension in image_extensions:
                    image_count += 1

            return image_count

        except FileNotFoundError:
            print(f"The folder {folder_path} does not exist.")
            return 0 
    def create_table(self, index):
        for widget in self.table_frame.winfo_children():
            widget.destroy()

        # Display the header and bind the tooltip to it
        header_label = tk.Label(self.table_frame, text=self.data_list[index][0], bg='#B7E1CD', padx=10, pady=5, font=('TkDefaultFont', 24))
        header_label.grid(row=0, column=0, sticky="nsew")
        header_label.bind("<Enter>", lambda event, idx=index: self.show_tooltip(event, idx))
        header_label.bind("<Leave>", self.hide_tooltip)

        # Display the rest of the cells excluding the last column (definition)
        for i, text in enumerate(self.data_list[index][1:-1]):
            bg_color = '#FFFFFF' if (i + 1) % 2 == 0 else '#F0F0F0'
            cell_label = tk.Label(self.table_frame, text=text, bg=bg_color, padx=10, pady=5, font=('TkDefaultFont', 18))
            cell_label.grid(row=i + 1, column=0, sticky="nsew")

        # Configure row and column weights for resizing
        self.table_frame.grid_rowconfigure(0, weight=1)
        self.table_frame.grid_columnconfigure(0, weight=1)

    def show_tooltip(self, event, index):
        if not hasattr(self, 'tooltip'):
            self.tooltip = tk.Toplevel(self.master)
            self.tooltip.wm_overrideredirect(True)
            self.tooltip.geometry(f"+{event.x_root+20}+{event.y_root+10}")
            label = tk.Label(self.tooltip, text=self.data_list[index][-1], background="white", borderwidth=1)
            label.pack()

    def hide_tooltip(self, event):
        if hasattr(self, 'tooltip'):
            self.tooltip.destroy()
            delattr(self, 'tooltip')


if __name__ == "__main__":
    root = tk.Tk()
    print("new main")
    root.geometry("480x800")
    app = TabooApp(root)
    root.mainloop()
    
