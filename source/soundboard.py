import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import numpy as np
import soundcard as sc
import wave
from pydub import AudioSegment
import os
import io

class SoundboardApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Virtual Soundboard")
        self.sound_buttons = []
        self.images = []  # Store image references to avoid garbage collection

        # Frame to hold buttons
        self.button_frame = tk.Frame(self.root)
        self.button_frame.pack(pady=20)

        # Add Sound button
        self.add_sound_button = tk.Button(self.root, text="Add Sound", command=self.add_sound)
        self.add_sound_button.pack(pady=10)

        # Use the default speaker for playback
        self.speaker = sc.default_speaker()
        
    def add_sound(self):
        # Open file dialog to select a sound file
        sound_file = filedialog.askopenfilename(
            title="Select Sound File",
            filetypes=(("WAV and MP3 Files", "*.wav;*.mp3"), ("All Files", "*.*"))
        )
        
        if sound_file:
            # Ask the user to select an image file for the button
            image_file = filedialog.askopenfilename(
                title="Select Image for Button",
                filetypes=(("Image Files", "*.png;*.jpg;*.jpeg"), ("All Files", "*.*"))
            )

            if image_file:
                # Load and resize the image
                image = Image.open(image_file)
                image = image.resize((80, 80), Image.LANCZOS)
                photo = ImageTk.PhotoImage(image)
                self.images.append(photo)  # Keep a reference to avoid garbage collection

                # Create a button with the image
                button = tk.Button(
                    self.button_frame, image=photo, command=lambda: self.play_sound(sound_file)
                )
                button.pack(side="top", fill="x", padx=5, pady=5)
                self.sound_buttons.append(button)

    def play_sound(self, file_path):
        # Handle both WAV and MP3 files
        if file_path.lower().endswith(".mp3"):
            # Convert MP3 to raw WAV data
            audio = AudioSegment.from_mp3(file_path)
            with io.BytesIO() as wav_io:
                audio.export(wav_io, format="wav")
                wav_io.seek(0)
                with wave.open(wav_io, 'rb') as wf:
                    sample_rate = wf.getframerate()
                    channels = wf.getnchannels()
                    audio_data = wf.readframes(wf.getnframes())
        else:
            # Load WAV file directly
            with wave.open(file_path, 'rb') as wf:
                sample_rate = wf.getframerate()
                channels = wf.getnchannels()
                audio_data = wf.readframes(wf.getnframes())

        # Convert raw audio data to NumPy array and normalize
        audio_array = np.frombuffer(audio_data, dtype=np.int16)
        audio_array = audio_array.astype(np.float32) / 32768.0  # Normalize to -1.0 to 1.0

        # Reshape for stereo or mono channels
        if channels == 2:
            audio_array = audio_array.reshape((-1, 2))

        # Play the audio data through the default speaker
        with self.speaker.player(samplerate=sample_rate, channels=channels) as player:
            player.play(audio_array)

if __name__ == "__main__":
    root = tk.Tk()
    app = SoundboardApp(root)
    root.mainloop()
