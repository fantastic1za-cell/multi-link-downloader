import os
import re
import yt_dlp
import instaloader

class BatchDownloader:
    def __init__(self, output_dir="downloads"):
        self.output_dir = os.path.abspath(output_dir)
        os.makedirs(self.output_dir, exist_ok=True)
        
        self.insta = instaloader.Instaloader(
            dirname_pattern=os.path.join(self.output_dir, "Instagram", "{target}"),
            download_videos=True,
            download_video_thumbnails=False,
            download_geotags=False,
            download_comments=False,
            save_metadata=False,
            compress_json=False
        )

    def is_instagram_profile(self, url: str) -> str | None:
        pattern = r"https?://(?:www\.)?instagram\.com/([a-zA-Z0-9_\.]+)/?$"
        match = re.match(pattern, url.strip().split('?')[0])
        if match:
            username = match.group(1)
            if username not in ["p", "reel", "reels", "stories", "tv", "explore"]:
                return username
        return None

    def download_instagram_profile(self, username: str, status_callback=None):
        if status_callback:
            status_callback(f"Fetching profile media for @{username}...")
        try:
            profile = instaloader.Profile.from_username(self.insta.context, username)
            for post in profile.get_posts():
                if status_callback:
                    status_callback(f"Downloading post {post.shortcode} from @{username}...")
                self.insta.download_post(post, target=username)
            return True, f"Successfully downloaded profile @{username}"
        except Exception as e:
            return False, f"Instagram Profile Error (@{username}): {str(e)}"

    def download_media_link(self, url: str, status_callback=None):
        url = url.strip()
        if not url:
            return False, "Empty URL"

        ig_username = self.is_instagram_profile(url)
        if ig_username:
            return self.download_instagram_profile(ig_username, status_callback)

        if status_callback:
            status_callback(f"Processing link: {url}")

        is_instagram = "instagram.com" in url
        if is_instagram:
            save_folder = os.path.join(self.output_dir, "Instagram", "Media")
        else:
            save_folder = os.path.join(self.output_dir, "Videos")

        os.makedirs(save_folder, exist_ok=True)

        ydl_opts = {
            'format': 'bestvideo+bestaudio/best',
            'outtmpl': os.path.join(save_folder, '%(uploader,channel,creator|Unknown)s_%(title)s_%(id)s.%(ext)s'),
            'merge_output_format': 'mp4',
            'quiet': True,
            'no_warnings': True,
            'nocheckcertificate': True,
            'ignoreerrors': False,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            return True, f"Successfully downloaded: {url}"
        except Exception as e:
            return False, f"Failed ({url}): {str(e)}"
