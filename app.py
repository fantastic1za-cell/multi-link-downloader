import streamlit as st
import os
import re
import glob
import yt_dlp
import instaloader

# Page configuration
st.set_page_config(
    page_title="Batch Link Downloader",
    page_icon="☁️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Dark glassmorphism styling
st.markdown("""
<style>
    .stApp { background-color: #0b1120; color: #f8fafc; }
    .header-card { background: rgba(30, 41, 59, 0.7); padding: 18px; border-radius: 16px; border: 1px solid rgba(255, 255, 255, 0.08); margin-bottom: 20px; }
    .stButton>button { background-color: #0284c7; color: white; border-radius: 12px; border: none; font-weight: 600; padding: 10px 20px; width: 100%; }
    .stButton>button:hover { background-color: #0369a1; }
</style>
""", unsafe_allow_html=True)

# Helper Functions
def classify_url(url: str) -> str:
    url_lower = url.lower()
    if "instagram.com" in url_lower:
        if "/reel/" in url_lower or "/tv/" in url_lower:
            return "Instagram Reel / Video"
        elif "/p/" in url_lower:
            return "Instagram Post"
        else:
            return "Instagram Profile"
    elif "twitter.com" in url_lower or "x.com" in url_lower:
        return "Twitter / X Video"
    elif "youtube.com" in url_lower or "youtu.be" in url_lower:
        return "YouTube Video"
    else:
        return "Generic Web Video"

def download_media(url: str, output_dir="downloads", progress_callback=None):
    os.makedirs(output_dir, exist_ok=True)
    downloaded_files = []

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
        'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'progress_hooks': [progress_hook],
        'quiet': True,
        'no_warnings': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            if 'requested_downloads' in info:
                for req in info['requested_downloads']:
                    downloaded_files.append(req['filepath'])
            else:
                filepath = ydl.prepare_filename(info)
                downloaded_files.append(filepath)
    except Exception as e:
        st.error(f"Engine download note: {e}")

    media_files = [f for f in downloaded_files if os.path.exists(f)]
    return media_files

# Header
st.markdown("""
<div class="header-card">
    <h2 style="margin:0; color:#ffffff; font-size: 1.4rem;">☁️ Batch Link Downloader</h2>
    <p style="margin:0; color:#94a3b8; font-size: 0.8rem;">iPhone 17 Pro Max Multi-Source Media Hub</p>
</div>
""", unsafe_allow_html=True)

# Navigation Tabs
tab1, tab2, tab3 = st.tabs(["📊 Media Dashboard", "⚙️ Destination & Quality", "💻 CLI Script Generator"])

if 'queue' not in st.session_state:
    st.session_state.queue = []
if 'destination' not in st.session_state:
    st.session_state.destination = "Local iOS Files (On My iPhone / Downloads)"

# --- TAB 1: MEDIA DASHBOARD ---
with tab1:
    st.subheader("📁 Multi-Platform Batch Input")
    st.caption("Supports YouTube, Twitter/X, Instagram, and Generic Web Video Links.")
    
    urls_input = st.text_area(
        "Paste links (one per line):",
        placeholder="https://www.instagram.com/reel/Cxxxxxx/\nhttps://x.com/username/status/12345678\nhttps://www.youtube.com/watch?v=xxxxxx",
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
                    media_type = classify_url(url)
                    st.session_state.queue.append({
                        "url": url,
                        "type": media_type,
                        "status": "Pending",
                        "progress": 0,
                        "speed": "0.0 MB/s",
                        "file_paths": []
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
            for idx, item in enumerate(st.session_state.queue):
                item['status'] = "Downloading..."
                
                status_box = st.empty()
                progress_bar = st.progress(0)
                
                def update_progress(percent, speed_mb):
                    item['progress'] = int(percent)
                    item['speed'] = f"{speed_mb:.1f} MB/s"
                    status_box.markdown(f"**Item #{idx+1}:** Downloading `{item['url']}` | ⚡ Speed: **{item['speed']}**")
                    progress_bar.progress(int(percent))

                files = download_media(item['url'], progress_callback=update_progress)
                if files:
                    item['status'] = "Completed ✅"
                    item['file_paths'] = files
                    item['progress'] = 100
                    item['speed'] = "0.0 MB/s"
                    status_box.success(f"Item #{idx+1} completed!")
                else:
                    item['status'] = "Completed / Check below ✅"
                    item['progress'] = 100
            
            st.success("🎉 Batch processing complete!")
            st.rerun()

        # Render Queue items and File Save buttons
        for idx, q_item in enumerate(st.session_state.queue):
            with st.container():
                st.markdown(f"**Item #{idx+1}:** `{q_item['url']}`")
                st.caption(f"Engine Target: {q_item['type']} | Status: {q_item['status']} | ⚡ Speed: {q_item['speed']}")
                st.progress(q_item['progress'])
                
                if q_item['file_paths']:
                    for f_idx, file_path in enumerate(q_item['file_paths']):
                        if os.path.exists(file_path):
                            file_name = os.path.basename(file_path)
                            mime_type = "image/jpeg" if file_name.endswith(('.jpg', '.jpeg', '.png')) else "video/mp4"
                            
                            with open(file_path, "rb") as f_bytes:
                                st.download_button(
                                    label=f"📥 Save File ({file_name}) to iPhone",
                                    data=f_bytes,
                                    file_name=file_name,
                                    mime=mime_type,
                                    key=f"dl_btn_{idx}_{f_idx}"
                                )

# --- TAB 2: DESTINATION & QUALITY ---
with tab2:
    st.subheader("💳 Destination & Security Rules")
    st.caption("Configure storage path rules.")
    
    dest_choice = st.radio(
        "Select Target Storage Location:",
        ["Local iOS Files (On My iPhone / Downloads)", "Google Drive Backup", "OneDrive Personal Vault"]
    )
    st.session_state.destination = dest_choice

# --- TAB 3: CLI SCRIPT GENERATOR ---
with tab3:
    st.subheader("⚙️ Zero-Prompt Python CLI Script")
    st.code("""import yt_dlp

def download(urls):
    with yt_dlp.YoutubeDL({'outtmpl': 'downloads/%(title)s.%(ext)s'}) as ydl:
        ydl.download(urls)

download(["https://x.com/status/123456"])""", language="python")
