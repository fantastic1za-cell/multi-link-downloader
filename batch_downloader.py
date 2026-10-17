import os
import re
import glob
import yt_dlp

class BatchDownloader:
    def __init__(self, output_dir="downloads"):
        self.output_dir = os.path.abspath(output_dir)
        os.makedirs(self.output_dir, exist_ok=True)

    def download_url(self, url, progress_callback=None):
        """
        Downloads a URL using yt-dlp and returns the path to the downloaded file.
        Passes progress updates to an optional callback function.
        """
        downloaded_files = []

        def my_hook(d):
            if d['status'] == 'downloading':
                total = d.get('total_bytes') or d.get('total_bytes_estimate') or 0
                downloaded = d.get('downloaded_bytes', 0)
                speed = d.get('speed', 0)
                
                percent = (downloaded / total * 100) if total > 0 else 0
                speed_mb = (speed / (1024 * 1024)) if speed else 0.0
                
                if progress_callback:
                    progress_callback(percent, speed_mb)

        ydl_opts = {
            'outtmpl': os.path.join(self.output_dir, '%(title)s.%(ext)s'),
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'progress_hooks': [my_hook],
            'quiet': True,
            'no_warnings': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            if 'requested_downloads' in info:
                for req in info['requested_downloads']:
                    downloaded_files.append(req['filepath'])
            else:
                filepath = ydl.prepare_filename(info)
                downloaded_files.append(filepath)

        return downloaded_files[0] if downloaded_files and os.path.exists(downloaded_files[0]) else None
