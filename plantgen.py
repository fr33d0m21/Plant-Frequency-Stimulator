# Copyright (C) 2023 Daniel Boissonneault
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import tkinter as tk
from tkinter import ttk
from pydub.playback import play as play_sound
import threading
from pydub import AudioSegment
from pydub.exceptions import CouldntDecodeError
import numpy as np
import os
import simpleaudio as sa
from ttkthemes import ThemedTk
from functools import partial
import openai
import os
import sys
import json


openai.api_key = "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"

def ask_gpt(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # Change to "gpt-4" if you have early access
        messages=[
            {"role": "system", "content": "You are a Sound Horticulturest expert."},
            {"role": "user", "content": "List the best frequencies for Cell Activation, Seed Germination, App Growth, Biomass Production, General Stimulation, Stress Reduction, Photosynthesis Enhancement, Flowering Induction, Fruit Development, and Disease Resistance."},
            {"role": "user", "content": prompt},
        ]
    )
    answer = response['choices'][0]['message']['content'].strip()
    return answer

def update_ui_with_gpt_response(prompt):
    answer = ask_gpt(prompt)
    # Update the UI with the answer, e.g., insert the answer into a Text widget

def on_ask_gpt_button_click():
    prompt = get_user_input()  # Replace this with the function to get user input from the app
    thread = threading.Thread(target=update_ui_with_gpt_response, args=(prompt,))
    thread.start()


def update_status_label(text):
    status_label.config(text=text)
    
def play_tone(freq, duration_minutes_lambda, mode_lambda):
    duration_minutes = duration_minutes_lambda()
    mode = mode_lambda()
    print(duration_minutes)

    duration_seconds = min(duration_minutes * 60, 600)  # Duration of the tone in seconds, capped at 10 minutes
    sample_rate = 22050  # Sample rate of the generated sound
    volume = 0.5  # Volume (0 to 1)

    samples = np.linspace(0, duration_seconds, num=int(sample_rate * duration_seconds), endpoint=False)
    sine_wave = np.sin(2 * np.pi * freq * samples / sample_rate)

    sine_wave = (sine_wave * 32767 * volume).astype(np.int16)

    if mode == 'binaural':
        # Create a second sine wave with a slight frequency difference for the right ear
        freq_right = freq + 10
        sine_wave_right = np.sin(2 * np.pi * freq_right * samples / sample_rate)
        sine_wave_right = (sine_wave_right * 32767 * volume).astype(np.int16)
        sine_wave = np.column_stack((sine_wave, sine_wave_right))
    elif mode == 'isochronic':
        isochronic_rate = 7  # Set the isochronic rate (e.g., 7 Hz)
        isochronic_wave = np.sin(2 * np.pi * isochronic_rate * samples / sample_rate)
        sine_wave = (sine_wave + isochronic_wave) / 2

    audio_segment = AudioSegment(
        sine_wave.tobytes(),
        frame_rate=sample_rate,
        sample_width=sine_wave.dtype.itemsize,
        channels=1,
    )

    app.after(0, update_status_label, "Playing")

    audio_data = audio_segment.get_array_of_samples()
    audio_data_np = np.array(audio_data, dtype=np.int16)

    play_obj = sa.play_buffer(audio_data_np, 1, 2, sample_rate)

    play_obj.wait_done()

    app.after(0, update_status_label, "Stopped")




def play_tone_thread(freq, duration_minutes, mode):
    threading.Thread(target=partial(play_tone, freq, duration_minutes, mode)).start()


def on_slider_change(value, frequency_label):
    frequency_label["text"] = f"Frequency: {int(float(value))} Hz"

def duration_minutes_lambda():
    duration_str = duration_entry.get()
    if duration_str:
        return float(duration_str)
    else:
        return 0.0

def mode_lambda():
    return mode_var.get()


app = ThemedTk(theme="arc")
app.title("Plant Frequency Stimulator")

# Part 2

# Create a frame for plant-related frequencies
plant_frame = ttk.LabelFrame(app, text="Plant Frequencies")
plant_frame.grid(row=0, column=0, padx=10, pady=10)

freq_data = [
    (50, "Cell Activation"),
    (100, "Seed Germination"),
    (200, "App Growth"),
    (300, "Biomass Production"),
    (440, "General Stimulation"),
    (500, "Stress Reduction"),
    (600, "Photosynthesis Enhancement"),
    (700, "Flowering Induction"),
    (800, "Fruit Development"),
    (900, "Disease Resistance"),
]

for i, (freq, label) in enumerate(freq_data):
    row = i + 3
    button = ttk.Button(
        plant_frame,
        text=label,
        command=partial(
            play_tone_thread,
            freq,
            duration_minutes_lambda,
            mode_lambda
        )
    )
    button.grid(row=row, column=1, padx=5, pady=5)

# Create a frame for tone settings
settings_frame = ttk.LabelFrame(app, text="Tone Settings")
settings_frame.grid(row=0, column=1, padx=10, pady=10)

mode_label = ttk.Label(settings_frame, text="Mode:")
mode_label.grid(row=1, column=0, padx=5, pady=5)

mode_var = tk.StringVar()
mode_var.set("mono")

mode_mono_button = ttk.Radiobutton(settings_frame, text="Mono", variable=mode_var, value="mono")
mode_mono_button.grid(row=1, column=1, padx=5, pady=5)

mode_binaural_button = ttk.Radiobutton(settings_frame, text="Binaural", variable=mode_var, value="binaural")
mode_binaural_button.grid(row=2, column=1, padx=5, pady=5)

mode_isochronic_button = ttk.Radiobutton(settings_frame, text="Isochronic", variable=mode_var, value="isochronic")
mode_isochronic_button.grid(row=3, column=1, padx=5, pady=5)





# Create a label and entry for setting the duration
duration_label = ttk.Label(app, text="Duration (minutes):")
duration_label.grid(row=i + 3, column=0, padx=5, pady=5)

duration_entry = ttk.Entry(app)
duration_entry.insert(0, "1")
duration_entry.grid(row=i + 4, column=0, padx=5, pady=5)



# Part 3

# Create a frame for AI interaction
ai_frame = ttk.LabelFrame(app, text="Type of plant & ask questions")
ai_frame.grid(row=0, column=2, padx=10, pady=10)

# Create an entry widget for user input
user_input = ttk.Entry(ai_frame, width=50)
user_input.grid(row=0, column=0, padx=5, pady=5)

# Remove the ask_button and update the ask_gpt_button to use the ask_question function
ask_gpt_button = ttk.Button(ai_frame, text="Ask", command=lambda: ask_question(user_input.get()))
ask_gpt_button.grid(row=0, column=1, padx=5, pady=5)

# Create a text widget to display the AI response
ai_response = tk.Text(ai_frame, width=60, height=10, wrap=tk.WORD)
ai_response.grid(row=1, column=0, columnspan=2, padx=5, pady=5)

def ask_question(question):
    prompt = f"Provide information on {question} and its optimal frequencies for different growth stages."
    answer = ask_gpt(prompt)
    ai_response.delete(1.0, tk.END)
    ai_response.insert(tk.END, answer)


# Create frequency slider
frequency_slider = ttk.Scale(app, from_=50, to=900, length=400, orient="horizontal", value=440, command=lambda value: on_slider_change(value, frequency_label))
frequency_slider.grid(row=1, column=0, pady=10)

# Create frequency label
frequency_label = ttk.Label(app, text="Frequency: 440 Hz")
frequency_label.grid(row=2, column=0, pady=5)

# Create a label to display the current slider frequency
frequency_label = ttk.Label(app, text=f"Frequency: {int(frequency_slider.get())} Hz")
frequency_label.grid(row=i + 2, column=0, padx=5, pady=5)

# Create a button for playing the slider frequency
play_slider_button = ttk.Button(
    app,
    text="Play",
    command=lambda: play_tone_thread(
        frequency_slider.get(),
        duration_minutes_lambda,
        mode_lambda
    )
)
play_slider_button.grid(row=5, column=0, pady=10)

# Create a label for showing the status of the tone player
status_label = ttk.Label(app, text="Stopped")
status_label.grid(row=6, column=0, pady=5)

app.mainloop()
