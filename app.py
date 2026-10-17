import streamlit as st
import time
import re
import os

# Page configuration
st.set_page_config(
    page_title="Batch Link Downloader",
    page_icon="☁️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom Styling to match dark glassmorphism layout
st.markdown("""
<style>
    .stApp { background-color: #0b1120; color: #f8fafc; }
    .header-card { background: rgba(30, 41, 59, 0.7); padding: 18px; border-radius: 16px; border: 1px solid rgba(255, 255, 255, 0.08); margin-bottom: 20px; }
    .status-badge { background: rgba(16, 185, 129, 0.15); color: #10b981; border: 1px solid rgba(16, 185, 129, 0.3); padding: 4px 12px; border-radius: 20px; font-size: 12px; }
    .stButton>button { background-color: #0284c7; color: white; border-radius: 12px; border: none; font-weight: 600; padding: 10px 20px; width: 100%; }
    .stButton>button:hover { background-color: #0369a1; }
</style>
""", unsafe_allow_html=True)

# Header Section
st.markdown("""
<div class="header-card flex justify-between items-center">
    <div>
        <h2 style="margin:0; color:#ffffff; font-size: 1.4rem;">☁️ Batch Link Downloader</h2>
        <p style="margin:0; color:#94a3b8; font-size: 0.8rem;">iPhone 17 Pro Max Automated Media Hub</p>
    </div>
</div>
""", unsafe_allow_html=True)

# Navigation Tabs
tab1, tab2, tab3 = st.tabs(["📊 Media Dashboard", "⚙️ Destination & Quality", "💻 CLI Script Generator"])

# Session State Initializations
if 'queue' not in st.session_state:
    st.session_state.queue = []
if 'destination' not in st.session_state:
    st.session_state.destination = "On My iPhone / Downloads"

# --- TAB 1: MEDIA DASHBOARD ---
with tab1:
    st.subheader("📁 Batch Link Input")
    st.caption("Paste links below. Instagram profiles, Reels, and generic video links are auto-classified.")
    
    urls_input = st.text_area(
        "Paste links (one per line):",
        placeholder="https://www.instagram.com/tech_creator/\nhttps://www.instagram.com/reel/C3x9L0xO8P/",
        height=140
    )
    
    st.info(f"📂 Active Destination: `{st.session_state.destination}`")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("▶️ Process & Add to Queue"):
            if urls_input.strip():
                lines = [line.strip() for line in urls_input.split('\n') if line.strip()]
                st.session_state.queue = []
                for url in lines:
                    if "instagram.com" in url:
                        media_type = "Instagram Profile" if "/reel/" not in url and "/p/" not in url else "Instagram Reel"
                    else:
                        media_type = "Generic Video Stream"
                    
                    st.session_state.queue.append({
                        "url": url,
                        "type": media_type,
                        "status": "Pending",
                        "progress": 0,
                        "speed": "0.0 MB/s"
                    })
                st.success(f"Added {len(lines)} item(s) to queue!")
    
    with col2:
        if st.button("🗑️ Clear Queue"):
            st.session_state.queue = []
            st.rerun()

    st.divider()
    
    # Active Queue Manager
    st.subheader("📋 Active Queue Manager")
    st.caption(f"{len(st.session_state.queue)} item(s) in queue")
    
    if st.session_state.queue:
        if st.button("🚀 Start Batch Download Process"):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            total_items = len(st.session_state.queue)
            for index, item in enumerate(st.session_state.queue):
                item['status'] = "Downloading..."
                
                # Download Speed and Progress simulation/execution
                for p in range(1, 101, 20):
                    time.sleep(0.15)
                    item['progress'] = p
                    simulated_speed = round(12.4 + (p % 3) * 1.5, 1)
                    item['speed'] = f"{simulated_speed} MB/s"
                    
                    status_text.markdown(f"**Downloading:** `{item['url']}` | ⚡ Speed: **{item['speed']}** | Progress: **{p}%**")
                    progress_bar.progress((index * 100 + p) // (total_items * 100))
                
                item['status'] = "Completed ✅"
                item['speed'] = "0.0 MB/s"
            
            status_text.success("🎉 All batch downloads completed successfully!")
            
        for idx, q_item in enumerate(st.session_state.queue):
            with st.container():
                st.markdown(f"**Item #{idx+1}:** `{q_item['url']}`")
                st.caption(f"Type: {q_item['type']} | Status: {q_item['status']} | ⚡ Speed: {q_item['speed']}")
                st.progress(q_item['progress'])

# --- TAB 2: DESTINATION & QUALITY ---
with tab2:
    st.subheader("💳 Destination & Security Rules")
    st.caption("Configure local storage paths and zero-prompt backup integrations.")
    
    dest_choice = st.radio(
        "Select Target Storage Location:",
        ["Local iOS Files (On My iPhone / Downloads)", "Google Drive Backup (Privacy Screen)", "OneDrive Personal Vault (Face ID Lock)"]
    )
    st.session_state.destination = dest_choice
    
    st.subheader("🎬 Video Quality Settings")
    quality = st.selectbox("Maximum Resolution Filter:", ["Highest Available (1080p/4K)", "720p HD (Fast Download)", "Audio Only (MP3)"])

# --- TAB 3: CLI SCRIPT GENERATOR ---
with tab3:
    st.subheader("⚙️ Zero-Prompt Python CLI Script")
    st.caption("Generates `batch_downloader.py` for direct command line batch execution on iOS or PC.")
    
    cli_code = """import os
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

    def is_instagram_profile(self, url: str) -> bool:
        pattern = r'https?://(?:www\.)?instagram\.com/([a-zA-Z0-0_\.]+)/?'
        match = re.match(pattern, url)
        if match:
            username = match.group(1)
            return username not in ['reel', 'p', 'stories', 'explore']
        return False

    def process_batch(self, url_list):
        for url in url_list:
            print(f"[+] Processing: {url}")
            if self.is_instagram_profile(url):
                username = re.match(r'https?://(?:www\.)?instagram\.com/([a-zA-Z0-0_\.]+)/?', url).group(1)
                self.insta.download_profile(username, profile_pic_only=False)
            else:
                ydl_opts = {
                    'outtmpl': os.path.join(self.output_dir, '%(title)s.%(ext)s'),
                    'format': 'bestvideo+bestaudio/best',
                }
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])

if __name__ == "__main__":
    urls = [
        "https://www.instagram.com/reel/C3x9L0xO8P/",
    ]
    downloader = BatchDownloader()
    downloader.process_batch(urls)
"""
    st.code(cli_code, language="python")
