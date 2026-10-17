import os
import re
import glob
import yt_dlp
import instaloader

class BatchDownloader:
    def __init__(self, output_dir="downloads"):
        self.output_dir = os.path.abspath(output_dir)
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Instaloader setup for Instagram photos, posts & full profiles
        self.loader = instaloader.Instaloader(
            dirname_pattern=os.path.join(self.output_dir, "Instagram", "{target}"),
            download_videos=True,
            download_video_thumbnails=False,
            download_geotags=False,
            download_comments=False,
            save_metadata=False,
            compress_json=False
        )

    def classify_url(self, url: str) -> str:
        """Classifies input URL to select optimal download engine."""
        url_lower = url.lower()
        if "instagram.com" in url_lower:
            if "/reel/" in url_lower or "/tv/" in url_lower:
                return "Instagram Reel / Video"
            elif "/p/" in url_lower:
                return "Instagram Post (Photo/Carousel)"
            else:
                return "Instagram Full Profile"
        elif "twitter.com" in url_lower or "x.com" in url_lower:
            return "Twitter / X Video"
        elif "youtube.com" in url_lower or "youtu.be" in url_lower:
            return "YouTube Video Stream"
        else:
            return "Generic Web Video / Stream"

    def download_url(self, url: str, progress_callback=None):
        """Routes link to yt-dlp or instaloader and returns list of downloaded file paths."""
        link_type = self.classify_url(url)
        downloaded_files = []

        # ENGINE A: Instaloader for Instagram Photos, Carousels & Full Profiles
        if link_type in ["Instagram Post (Photo/Carousel)", "Instagram Full Profile"]:
            if link_type == "Instagram Full Profile":
                match = re.search(r'instagram\.com/([a-zA-Z0-9_\.]+)', url)
                if match:
                    username = match.group(1)
                    profile = instaloader.Profile.from_username(self.loader.context, username)
                    target_dir = os.path.join(self.output_dir, "Instagram", username)
                    for post in profile.get_posts():
                        self.loader.download_post(post, target=username)
                    downloaded_files = glob.glob(os.path.join(target_dir, "*.*"))
            else:
                # Single Post or Photo Carousel
                match = re.search(r'instagram\.com/p/([^/]+)', url)
                if match:
                    shortcode = match.group(1)
                    post = instaloader.Post.from_shortcode(self.loader.context, shortcode)
                    target_dir = os.path.join(self.output_dir, "Instagram", post.owner_username)
                    self.loader.download_post(post, target=post.owner_username)
                    downloaded_files = glob.glob(os.path.join(target_dir, "*.*"))

        # ENGINE B: yt-dlp for YouTube, Twitter/X, Instagram Reels & Generic Videos
        else:
            def progress_hook(d):
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
                'progress_hooks': [progress_hook],
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

        # Filter out metadata json/txt files and return media files
        media_files = [f for f in downloaded_files if f.endswith(('.mp4', '.jpg', '.png', '.jpeg', '.m4a', '.webm')) and os.path.exists(f)]
        return media_files
