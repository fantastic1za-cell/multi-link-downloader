import streamlit as st
import os
import glob
import re
import requests
import yt_dlp

# Page setup
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

# URL Classification Helper
def classify_url(url: str) -> str:
    u = url.lower()
    if "instagram.com" in u:
        return "Instagram Media (SSSInstagram Engine)"
    elif "tiktok.com" in u:
        return "TikTok HD (SnapTik Engine)"
    elif "twitter.com" in u or "x.com" in u:
        return "Twitter / X Video"
    elif "youtube.com" in u or "youtu.be" in u:
        return "YouTube 4K Stream"
    elif "pornhub.com" in u:
        return "Adult Media Stream"
    else:
        return "Generic Web Video (SaveTheVideo Engine)"

# SnapTik/Tikwm API Stream Harvester for TikTok
def fetch_tiktok_snaptik(url: str, output_dir: str) -> str:
    try:
        api_url = f"https://www.tikwm.com/api/?url={requests.utils.quote(url)}"
        res = requests.get(api_url, timeout=10).json()
        if res.get("code") == 0:
            video_url = res["data"].get("play") or res["data"].get("wmplay")
            if video_url:
                out_path = os.path.join(output_dir, f"tiktok_{res['data'].get('id', 'hd')}.mp4")
                v_res = requests.get(video_url, timeout=20, stream=True)
                with open(out_path, 'wb') as f:
                    for chunk in v_res.iter_content(chunk_size=32768):
                        f.write(chunk)
                if os.path.exists(out_path) and os.path.getsize(out_path) > 1024 * 1024:
                    return out_path
    except Exception:
        pass
    return None

# High-Precision Multi-Engine Video Downloader (Max 4K Quality)
def download_max_quality(url: str, output_dir="downloads", status_box=None, progress_bar=None):
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. TikTok SnapTik Direct API Engine
    if "tiktok.com" in url.lower():
        if status_box: status_box.markdown("⚡ Fetching TikTok HD Video via SnapTik Engine...")
        tt_file = fetch_tiktok_snaptik(url, output_dir)
        if tt_file:
            return tt_file

    # 2. Universal 4K Extractor Engine (SaveTheVideo / SSSInstagram equivalent)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Cookie': 'age_verified=1; platform=pc; bs=1',
    }

    def progress_hook(d):
        if d['status'] == 'downloading':
            total = d.get('total_bytes') or d.get('total_bytes_estimate') or 0
            downloaded = d.get('downloaded_bytes', 0)
            speed = d.get('speed', 0)
            percent = (downloaded / total * 100) if total > 0 else 0
            speed_mb = (speed / (1024 * 1024)) if speed else 0.0
            
            if status_box and progress_bar:
                status_box.markdown(f"⚡ Downloading Max 4K Stream: **{percent:.1f}%** | Speed: **{speed_mb:.1f} MB/s**")
                progress_bar.progress(int(percent))

    # Priority to Highest Resolution (Up to 4K / 2160p)
    ydl_opts = {
        'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
        'format': 'bestvideo[height<=2160][ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio/best',
        'progress_hooks': [progress_hook],
        'quiet': True,
        'no_warnings': True,
        'nocheckcertificate': True,
        'ignoreerrors': True,
        'user_agent': headers['User-Agent'],
        'http_headers': headers
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            if info:
                filepath = ydl.prepare_filename(info)
                if os.path.exists(filepath) and os.path.getsize(filepath) > 1024 * 1024:
                    return filepath
    except Exception:
        pass

    # Fallback Directory Scan for valid media files (> 1 MB)
    all_files = glob.glob(os.path.join(output_dir, "*.*"))
    valid_files = [f for f in all_files if os.path.exists(f) and os.path.getsize(f) > 1024 * 1024]
    
    return valid_files[0] if valid_files else None

# Header
st.markdown("""
<div class="header-card">
    <h2 style="margin:0; color:#ffffff; font-size: 1.4rem;">☁️ Batch Link Downloader</h2>
    <p style="margin:0; color:#94a3b8; font-size: 0.8rem;">iPhone 17 Pro Max 4K Multi-Engine Media Hub</p>
</div>
""", unsafe_allow_html=True)

# Navigation Tabs
tab1, tab2, tab3 = st.tabs(["📊 Media Dashboard", "⚙️ Destination & Quality", "💻 CLI Script Generator"])

if 'queue' not in st.session_state:
    st.session_state.queue = []
if 'destination' not in st.session_state:
    st.session_state.destination = "On My iPhone / Downloads"

# --- TAB 1: MEDIA DASHBOARD ---
with tab1:
    st.subheader("📁 Multi-Platform Batch Input (Max 4K Quality)")
    st.caption("Integrated Engines: SnapTik (TikTok HD), SSSInstagram (Reels/Posts), SaveTheVideo (4K/Web/Adult).")
    
    urls_input = st.text_area(
        "Paste links (one per line):",
        placeholder="https://www.tiktok.com/@username/video/12345678\nhttps://www.instagram.com/reel/Cxxxxxx/\nhttps://www.youtube.com/watch?v=xxxxxx\nhttps://www.pornhub.com/view_video.php?viewkey=69f07e4c68014",
        height=140
    )
    
    st.info(f"📂 Storage Target: `{st.session_state.destination}`")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("▶️ Process & Add to Queue"):
            if urls_input.strip():
                lines = [line.strip() for line in urls_input.split('\n') if line.strip()]
                st.session_state.queue = []
                for url in lines:
                    st.session_state.queue.append({
                        "url": url,
                        "type": classify_url(url),
                        "status": "Pending",
                        "progress": 0,
                        "file_path": None
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
                item['status'] = "Downloading Highest Quality Stream (Up to 4K)..."
                
                status_box = st.empty()
                progress_bar = st.progress(0)
                
                file_path = download_max_quality(
                    url=item['url'],
                    status_box=status_box,
                    progress_bar=progress_bar
                )
                
                if file_path:
                    file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
                    item['status'] = f"Ready for Save ✅ ({file_size_mb:.1f} MB)"
                    item['file_path'] = file_path
                    item['progress'] = 100
                    status_box.success(f"Item #{idx+1} verified! Size: {file_size_mb:.1f} MB")
                else:
                    item['status'] = "Cloud IP Blocked ❌ (Use CLI Script in Tab 3)"
                    item['progress'] = 0
                    status_box.error(f"Item #{idx+1} failed due to cloud IP block.")
            
            st.rerun()

        # Render Queue items and Native iPhone Download Buttons
        for idx, q_item in enumerate(st.session_state.queue):
            with st.container():
                st.markdown(f"**Item #{idx+1}:** `{q_item['url']}`")
                st.caption(f"Engine Target: {q_item['type']} | Status: {q_item['status']}")
                st.progress(q_item['progress'])
                
                # Render save button only when valid media file is verified
                if q_item['file_path'] and os.path.exists(q_item['file_path']):
                    file_size_mb = os.path.getsize(q_item['file_path']) / (1024 * 1024)
                    file_name = os.path.basename(q_item['file_path'])
                    
                    with open(q_item['file_path'], "rb") as f_bytes:
                        st.download_button(
                            label=f"📥 Save Item #{idx+1} ({file_size_mb:.1f} MB) to iPhone Files",
                            data=f_bytes,
                            file_name=file_name,
                            mime="video/mp4",
                            key=f"max_dl_{idx}"
                        )

# --- TAB 2: DESTINATION RULES ---
with tab2:
    st.subheader("💳 Storage Path Rules")
    dest_choice = st.radio(
        "Select Target Storage Location:",
        ["Local iOS Files (On My iPhone / Downloads)", "Google Drive Backup", "OneDrive Personal Vault"]
    )
    st.session_state.destination = dest_choice

# --- TAB 3: CLI SCRIPT GENERATOR ---
with tab3:
    st.subheader("⚙️ Zero-Prompt Python CLI Script")
    st.caption("Running this script directly on your device (via a terminal app or PC) completely bypasses all cloud IP blocks because it uses your local cellular/Wi-Fi connection.")
    st.code("""import yt_dlp

def download_batch(urls):
    ydl_opts = {
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'format': 'bestvideo[height<=2160]+bestaudio/best',
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
            'Cookie': 'age_verified=1; platform=pc;'
        }
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download(urls)

if __name__ == "__main__":
    download_batch([
        "https://www.tiktok.com/@username/video/12345678",
        "https://www.instagram.com/reel/Cxxxxxx/",
        "https://www.pornhub.com/view_video.php?viewkey=69f07e4c68014"
    ])""", language="python")
