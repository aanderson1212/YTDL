import os
import sys
import threading
from tkinter import *
from tkinter import filedialog
import tkinter as tk
from tkinter.ttk import Progressbar
from yt_dlp import YoutubeDL

project_dir = os.path.dirname(os.path.abspath(__file__))
if getattr(sys, 'frozen', False):
    base_path = sys._MEIPASS
else:
    base_path = os.path.abspath(".")

ffmpeg_path = os.path.join(base_path, "ffmpeg.exe")

class VideoDownloader:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube Video Downloader")
        self.create_widgets()

    def create_widgets(self):
        title_label = Label(self.root, text="YouTube Video Downloader", font=("Arial", 16))
        title_label.pack(pady=10)
        self.entries_frame = Frame(self.root)
        self.entries_frame.pack()

        self.url_label = Label(self.root, text="Enter URLs in the spaces above:", font=("Arial", 11))
        self.url_label.pack(pady=5)
        self.totalEntries = 5
        self.url_entries = [
            Entry(self.entries_frame, width=50, borderwidth=2, relief='groove')
            for _ in range(self.totalEntries)
        ]
        for entry in self.url_entries:
            entry.pack(pady=5)


        self.location_label = Label(self.root, text="Download Location:")
        self.location_label.pack()

        self.location_entry = Entry(self.root, width=60, borderwidth=2, relief='groove')
        self.location_entry.pack(pady=5)

        self.browse_button = Button(self.root, text="Browse", command=self.browse_location)
        self.browse_button.pack(pady=5)

        self.mp3_var = IntVar()
        self.mp3_checkbox = Checkbutton(self.root, text="Download as MP3", variable=self.mp3_var)
        self.mp3_checkbox.pack(pady=5)

        self.playlist_var = IntVar()
        self.playlist_checkbox = Checkbutton(self.root, text="Download as Playlist", variable=self.playlist_var, command=self.update_url_entries)
        self.playlist_checkbox.pack(pady=5)

        self.download_button = Button(self.root, text="Download", command=self.start_download_thread, bg='blue', fg='white')
        self.download_button.pack(pady=10)

        self.progress = DoubleVar()
        self.progressbar = Progressbar(self.root, variable=self.progress, maximum=100)
        self.progressbar.pack(pady=5)

        self.completion_label = Label(self.root, text="", fg="green")
        self.completion_label.pack(pady=10)

        self.error_label = Label(self.root, text="", fg="red")
        self.error_label.pack()

        self.version_label = Label(self.root, text="Version 0.5", fg="blue")
        self.version_label.pack()
        self.version_label.place(x=0, y=480)
    def update_url_entries(self):
        if self.playlist_var.get() == 1:
            self.url_label.config(text="Enter the URL of the first video in the playlist above:")
        else:
            self.url_label.config(text="Enter URLs in the spaces above:")
        for entry in self.url_entries:
            entry.destroy()

        self.totalEntries = 1 if self.playlist_var.get() else 5

        self.url_entries = [
            Entry(self.entries_frame, width=50, borderwidth=2, relief='groove')
            for _ in range(self.totalEntries)
        ]

        for entry in self.url_entries:
            entry.pack(pady=5)
    def browse_location(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.location_entry.delete(0, END)
            self.location_entry.insert(0, folder_selected)

    def start_download_thread(self):
        download_thread = threading.Thread(target=self.download_videos)
        download_thread.start()

    def progress_hook(self, d):
        if d['status'] == 'downloading':
            if 'downloaded_bytes' in d and 'total_bytes' in d:
                percent = d['downloaded_bytes'] / d['total_bytes'] * 100
                self.progress.set(percent)

    def download_videos(self):
        self.completion_label.config(text="Downloading...", fg='Red')
        self.error_label.config(text="")
        urls = [entry.get().strip() for entry in self.url_entries if entry.get().strip()]
        download_path = self.location_entry.get().strip() or os.getcwd()

        if not urls:
            self.error_label.config(text="No valid URLs provided.")
            return

        for url in urls:
            ydl_opts = {
                'format': 'bestaudio/best' if self.mp3_var.get() else 'best',
                'outtmpl': os.path.join(download_path, '%(title)s.%(ext)s'),
                'progress_hooks': [self.progress_hook],
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }] if self.mp3_var.get() else None,
                'ffmpeg_location': ffmpeg_path,
                'noplaylist': False if self.playlist_var.get() == 1 else True,
            }

            try:
                with YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
                self.progress.set(100)
            except Exception as e:
                self.error_label.config(text=f"Error downloading {url}: {str(e)}")
                self.progress.set(0)
        self.completion_label.config(text="Download complete!", fg="Green")

if __name__ == "__main__":
    root = Tk()
    app = VideoDownloader(root)
    root.resizable(width=False, height=False)
    root.iconbitmap('icon.ico')
    root.mainloop()
