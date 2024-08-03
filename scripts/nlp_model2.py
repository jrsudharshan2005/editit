import cv2
import numpy as np
import speech_recognition as sr
from tkinter import Tk, Label, Button, filedialog, Canvas, messagebox, simpledialog
from PIL import Image, ImageTk
from moviepy.editor import VideoFileClip, AudioFileClip, CompositeAudioClip
from pydub import AudioSegment
from threading import Thread
import os
import tempfile

class VideoEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Video Editor")

        self.video_path = None
        self.trimmed_path = None
        self.audio_path = None
        self.video_capture = None
        self.video_writer = None
        self.is_playing = True
        self.frame = None
        self.current_frame = 0
        self.fps = 30
        self.command = None
        self.blur_applied = False  # State for blur effect

        self.create_widgets()
        self.start_voice_recognition()

    def create_widgets(self):
        # Canvas for video display
        self.canvas = Canvas(self.root, width=640, height=480)
        self.canvas.pack()

        # Load button images
        self.play_img = ImageTk.PhotoImage(Image.open(r"C:\Users\jrsud\OneDrive\Documents\vedeo editor\venv\data\icons\icons8-play-50.png").resize((50, 50)))
        self.pause_img = ImageTk.PhotoImage(Image.open(r"C:\Users\jrsud\OneDrive\Documents\vedeo editor\venv\data\icons\icons8-play-50.png").resize((50, 50)))
        self.save_img = ImageTk.PhotoImage(Image.open(r"C:\Users\jrsud\OneDrive\Documents\vedeo editor\venv\data\icons\icons8-save-96.png").resize((50, 50)))
        self.blur_img = ImageTk.PhotoImage(Image.open(r"C:\Users\jrsud\OneDrive\Documents\vedeo editor\venv\data\icons\icons8-blur-64.png").resize((50, 50)))
        self.clear_img = ImageTk.PhotoImage(Image.open(r"C:\Users\jrsud\OneDrive\Documents\vedeo editor\venv\data\icons\icons8-blur-64.png").resize((50, 50)))
        self.trim_img = ImageTk.PhotoImage(Image.open(r"C:\Users\jrsud\OneDrive\Documents\vedeo editor\venv\data\icons\icons8-trim-48.png").resize((50, 50)))
        self.volume_img = ImageTk.PhotoImage(Image.open(r"C:\Users\jrsud\OneDrive\Documents\vedeo editor\venv\data\icons\icons8-volume-64.png").resize((50, 50)))
        self.music_img = ImageTk.PhotoImage(Image.open(r"C:\Users\jrsud\OneDrive\Documents\vedeo editor\venv\data\icons\icons8-volume-64.png").resize((50, 50)))
        self.play_trimmed_img = ImageTk.PhotoImage(Image.open(r"C:\Users\jrsud\OneDrive\Documents\vedeo editor\venv\data\icons\icons8-play-64.png").resize((50, 50)))
        self.upload_video_img = ImageTk.PhotoImage(Image.open(r"C:\Users\jrsud\OneDrive\Documents\vedeo editor\venv\data\icons\icons8-upload-48.png").resize((50, 50)))
        self.upload_audio_img = ImageTk.PhotoImage(Image.open(r"C:\Users\jrsud\OneDrive\Documents\vedeo editor\venv\data\icons\icons8-upload-music-24.png").resize((50, 50)))

        # Buttons with icons
        self.play_pause_button = Button(self.root, image=self.play_img, command=self.toggle_play_pause)
        self.play_pause_button.pack(side="left", padx=5, pady=5)

        self.blur_button = Button(self.root, image=self.blur_img, command=self.toggle_blur)
        self.blur_button.pack(side="left", padx=5, pady=5)

        Button(self.root, image=self.save_img, command=self.save_video).pack(side="left", padx=5, pady=5)
        Button(self.root, image=self.clear_img, command=self.clear_frame).pack(side="left", padx=5, pady=5)
        Button(self.root, image=self.trim_img, command=self.trim_video).pack(side="left", padx=5, pady=5)
        Button(self.root, image=self.volume_img, command=self.adjust_volume).pack(side="left", padx=5, pady=5)
        Button(self.root, image=self.music_img, command=self.add_background_music).pack(side="left", padx=5, pady=5)
        Button(self.root, image=self.play_trimmed_img, command=self.play_trimmed_video).pack(side="left", padx=5, pady=5)
        Button(self.root, image=self.upload_video_img, command=self.upload_video).pack(side="left", padx=5, pady=5)
        Button(self.root, image=self.upload_audio_img, command=self.upload_audio).pack(side="left", padx=5, pady=5)

        # Label for displaying timeline
        self.timeline_label = Label(self.root, text="Timeline: 0.00/0.00 seconds")
        self.timeline_label.pack()

        # Start video processing in a separate thread
        self.root.after(100, self.process_video)

    def start_voice_recognition(self):
        self.recognizer_thread = Thread(target=self.recognize_speech)
        self.recognizer_thread.daemon = True
        self.recognizer_thread.start()

    def recognize_speech(self):
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            while True:
                try:
                    print("Listening for commands...")
                    audio = recognizer.listen(source)
                    command = recognizer.recognize_google(audio).lower()
                    print(f"You said: {command}")
                    self.process_command(command)
                except sr.UnknownValueError:
                    continue
                except sr.RequestError:
                    print("Speech recognition error")
                    continue

    def process_command(self, command):
        if "pause" in command or "play" in command:
            self.toggle_play_pause()
        elif "save" in command:
            self.save_video()
        elif "blur" in command:
            self.toggle_blur()
        elif "clear" in command:
            self.clear_frame()
        elif "trim" in command:
            self.trim_video()
        elif "volume" in command:
            self.adjust_volume()
        elif "background music" in command:
            self.add_background_music()
        elif "play trimmed video" in command:
            self.play_trimmed_video()
        elif "upload video" in command:
            self.upload_video()
        elif "upload audio" in command:
            self.upload_audio()

    def toggle_play_pause(self):
        self.is_playing = not self.is_playing
        if self.is_playing:
            self.play_pause_button.config(image=self.pause_img)
        else:
            self.play_pause_button.config(image=self.play_img)

    def toggle_blur(self):
        self.blur_applied = not self.blur_applied
        if self.blur_applied:
            self.blur_button.config(relief="sunken")  # Change button appearance to indicate active state
        else:
            self.blur_button.config(relief="raised")  # Change button appearance to indicate inactive state

    def upload_video(self):
        if self.video_path is None:
            file_path = filedialog.askopenfilename(title="Select a Video File", filetypes=[("Video Files", "*.mp4 *.avi")])
            if file_path:
                self.video_path = file_path
                self.video_capture = cv2.VideoCapture(self.video_path)
                self.fps = int(self.video_capture.get(cv2.CAP_PROP_FPS))
                self.current_frame = 0
                messagebox.showinfo("Info", f"Video uploaded: {self.video_path}")
        else:
            messagebox.showinfo("Info", "Video already uploaded.")

    def upload_audio(self):
        if self.audio_path is None:
            file_path = filedialog.askopenfilename(title="Select an Audio File", filetypes=[("Audio Files", "*.mp3 *.wav")])
            if file_path:
                self.audio_path = file_path
                messagebox.showinfo("Info", f"Audio uploaded: {self.audio_path}")
        else:
            messagebox.showinfo("Info", "Audio already uploaded.")

    def save_video(self):
        if self.video_writer:
            self.video_writer.release()
            self.video_writer = None
            messagebox.showinfo("Info", "Video saved.")

    def clear_frame(self):
        if self.frame is not None:
            self.frame = np.zeros_like(self.frame)

    def trim_video(self):
        if self.video_path:
            start_time = simpledialog.askfloat("Input", "Enter start time in seconds:")
            end_time = simpledialog.askfloat("Input", "Enter end time in seconds:")
            if start_time is not None and end_time is not None:
                self.trimmed_path = "trimmed_video.mp4"
                clip = VideoFileClip(self.video_path).subclip(start_time, end_time)
                clip.write_videofile(self.trimmed_path, codec="libx264")
                messagebox.showinfo("Info", f"Video trimmed and saved as {self.trimmed_path}")

    def adjust_volume(self):
        if self.audio_path:
            volume_change_dB = simpledialog.askfloat("Input", "Enter volume change in dB:")
            if volume_change_dB is not None:
                audio = AudioSegment.from_file(self.audio_path)
                audio = audio + volume_change_dB
                adjusted_path = "adjusted_volume_audio.mp3"
                audio.export(adjusted_path, format="mp3")
                messagebox.showinfo("Info", f"Volume adjusted and saved as {adjusted_path}")

    def add_background_music(self):
        if self.audio_path and self.video_path:
            output_path = "video_with_music.mp4"
            video_clip = VideoFileClip(self.video_path)
            audio_clip = AudioFileClip(self.audio_path)
            
            # Trim audio to match the video length if necessary
            if audio_clip.duration > video_clip.duration:
                audio_clip = audio_clip.subclip(0, video_clip.duration)
                
            final_audio = CompositeAudioClip([video_clip.audio, audio_clip])
            final_clip = video_clip.set_audio(final_audio)
            final_clip.write_videofile(output_path, codec="libx264", audio_codec="aac")
            messagebox.showinfo("Info", f"Background music added. Output saved as {output_path}")

    def play_trimmed_video(self):
        if self.trimmed_path:
            os.startfile(self.trimmed_path)  # This is Windows-specific. For other platforms, use appropriate commands.

    def process_video(self):
        if self.is_playing and self.video_capture:
            ret, frame = self.video_capture.read()
            if ret:
                self.frame = frame
                self.current_frame = int(self.video_capture.get(cv2.CAP_PROP_POS_FRAMES))
                total_frames = int(self.video_capture.get(cv2.CAP_PROP_FRAME_COUNT))
                self.fps = int(self.video_capture.get(cv2.CAP_PROP_FPS))
                current_time = self.current_frame / self.fps
                total_time = total_frames / self.fps
                self.timeline_label.config(text=f"Timeline: {current_time:.2f}/{total_time:.2f} seconds")

                if self.blur_applied:
                    frame = self.apply_blur(frame)

                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                image = Image.fromarray(frame_rgb)
                self.photo_image = ImageTk.PhotoImage(image)  # Keep a reference to avoid garbage collection
                self.canvas.create_image(0, 0, anchor="nw", image=self.photo_image)

                # Schedule next frame update
                self.root.after(int(1000 / self.fps), self.process_video)
            else:
                self.video_capture.release()
                self.video_capture = None
                messagebox.showinfo("Info", "Video playback finished.")
        else:
            # Keep calling process_video even if paused
            self.root.after(100, self.process_video)


    def apply_blur(self, frame):
        return cv2.GaussianBlur(frame, (15, 15), 0)

def main():
    root = Tk()
    app = VideoEditor(root)
    root.mainloop()

if __name__ == "__main__":
    main()
