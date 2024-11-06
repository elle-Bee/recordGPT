import threading
import speech_recognition as sr
import tkinter as tk
from tkinter import messagebox, scrolledtext
from pydub import AudioSegment
from pydub.playback import play
import io

# Initialize recognizer
recognizer = sr.Recognizer()

is_listening = False
is_paused = False
last_words = []


def write_to_file(text):
    with open("content.txt", "a") as file:
        file.write(text + "\n")


def play_audio_segment(audio_data):
    audio_segment = AudioSegment.from_file(io.BytesIO(audio_data.get_wav_data()), format="wav")
    segment_to_play = audio_segment[:2000]
    play(segment_to_play)


def recognize_speech():
    global is_listening, is_paused, recognizer, last_words
    while is_listening:
        if is_paused:
            continue
        try:
            with sr.Microphone() as mic:
                recognizer.adjust_for_ambient_noise(mic, duration=0.2)
                audio = recognizer.listen(mic)
                text = recognizer.recognize_google(audio).lower()

                write_to_file(text)
                last_words.append(text)
                if len(last_words) > 10:
                    last_words.pop(0)

                update_last_words_display()

        except sr.UnknownValueError:
            recognizer = sr.Recognizer()
            continue


def update_last_words_display():
    last_words_display.config(state=tk.NORMAL)
    last_words_display.delete(1.0, tk.END)
    for word in last_words:
        last_words_display.insert(tk.END, word + "\n")
    last_words_display.config(state=tk.DISABLED)


def start_recognition():
    global is_listening, is_paused
    if not is_listening:
        is_listening = True
        is_paused = False
        threading.Thread(target=recognize_speech, daemon=True).start()
        status_label.config(text="Status: Listening...")


def pause_recognition():
    global is_paused
    if is_listening:
        is_paused = not is_paused
        status_label.config(text="Status: Paused" if is_paused else "Status: Listening...")


def stop_recognition():
    global is_listening
    if is_listening:
        is_listening = False
        status_label.config(text="Status: Stopped")
        messagebox.showinfo("Speech Recognition", "Stopped and saved content to content.txt")


# Setup Tkinter GUI
root = tk.Tk()
root.title("Speech Recognition App")

# Create buttons and labels
start_button = tk.Button(root, text="Start", command=start_recognition, width=10)
pause_button = tk.Button(root, text="Pause", command=pause_recognition, width=10)
stop_button = tk.Button(root, text="Stop", command=stop_recognition, width=10)
status_label = tk.Label(root, text="Status: Stopped", font=("Arial", 12))

# Create a scrolled text area to display the last 10 words
last_words_display = scrolledtext.ScrolledText(root, width=50, height=10, font=("Arial", 12), state=tk.DISABLED)
last_words_display.grid(row=1, column=0, columnspan=3, padx=10, pady=10)

# Place buttons in the GUI
start_button.grid(row=0, column=0, padx=10, pady=10)
pause_button.grid(row=0, column=1, padx=10, pady=10)
stop_button.grid(row=0, column=2, padx=10, pady=10)

# Place status label in the GUI
status_label.grid(row=2, column=0, columnspan=3, pady=10)

# Run the Tkinter event loop
root.mainloop()
