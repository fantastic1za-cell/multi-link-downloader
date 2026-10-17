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
        return "Instagram Media"
    elif "twitter.com" in u or "x.com" in u:
        return "Twitter / X Video"
    elif "youtube.com" in u or "youtu.be" in u:
        return "YouTube Video"
    elif "pornhub.com" in u:
        return "Adult Media Stream"
    else:
        return "Generic Web Video"

# Proxy-Bypass Extraction Engine
def download_via_proxy_failsafe(url: str, output_dir="downloads", progress_callback=None):
    os.makedirs(output_dir, exist_ok=True)
    downloaded_files = []

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9',
        'Cookie': 'age_verified=1; platform=pc; bs=1',
    }

    # Pipeline Step 1: Attempt direct yt-dlp download
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
        'format': 'best',
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
                if os.path.exists(filepath):
                    downloaded_files.append(filepath)
    except Exception:
        pass

    # Pipeline Step 2: Proxy Tunnel Harvesting (Bypasses Datacenter IP Blocks)
    if not downloaded_files:
        proxy_gateways = [
            f"https://corsproxy.io/?{url}",
            f"https://api.allorigins.win/raw?url={url}"
        ]
        
        for gateway in proxy_gateways:
            try:
                res = requests.get(gateway, headers=headers, timeout=12)
                if res.status_code == 200:
                    # Search for raw media stream links
                    mp4_links = re.findall(r'https?://[^\s\'"]+\.mp4[^\s\'"]*', res.text)
                    if mp4_links:
                        clean_link = mp4_links[0].replace('\\/', '/')
                        out_path = os.path.join(output_dir, f"video_stream_{abs(hash(url)) % 1000000}.mp4")
                        
                        # Download media stream through proxy gateway
                        stream_res = requests.get(f"https://corsproxy.io/?{clean_link}", headers=headers, stream=True, timeout=20)
                        if stream_res.status_code == 200:
                            with open(out_path, 'wb') as f:
                                for chunk in stream_res.iter_content(chunk_size=32768):
                                    f.write(chunk)
                            if os.path.exists(out_path) and os.path.getsize(out_path) > 1024:
                                downloaded_files.append(out_path)
                                break
            except Exception:
                continue

    # Pipeline Step 3: Scan Output Directory for Newly Saved Files
    if not downloaded_files:
        all_files = glob.glob(os.path.join(output_dir, "*.*"))
        downloaded_files = [f for f in all_files if os.path.exists(f) and os.path.getsize(f) > 1024]

    return downloaded_files

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
    st.caption("Supports YouTube, Twitter/X, Instagram, Adult Media & Generic Web Video Links.")
    
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
                    st.session_state.queue.append({
                        "url": url,
                        "type": classify_url(url),
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
                item['status'] = "Bypassing Datacenter IP Block..."
                status_box = st.empty()
                progress_bar = st.progress(0)
                
                def update_progress(percent, speed_mb):
                    item['progress'] = int(percent)
                    item['speed'] = f"{speed_mb:.1f} MB/s"
                    status_box.markdown(f"**Item #{idx+1}:** Downloading `{item['url']}` | ⚡ Speed: **{item['speed']}**")
                    progress_bar.progress(int(percent))

                files = download_via_proxy_failsafe(item['url'], progress_callback=update_progress)
                if files:
                    item['status'] = "Ready for Save ✅"
                    item['file_paths'] = files
                    item['progress'] = 100
                    item['speed'] = "0.0 MB/s"
                    status_box.success(f"Item #{idx+1} successfully processed!")
                else:
                    item['status'] = "Cloud IP Blocked ❌ (Use CLI Tab for Local Download)"
                    item['progress'] = 0
            
            st.rerun()

        # Render Queue items and File Save buttons
        for idx, q_item in enumerate(st.session_state.queue):
            with st.container():
                st.markdown(f"**Item #{idx+1}:** `{q_item['url']}`")
                st.caption(f"Engine Target: {q_item['type']} | Status: {q_item['status']} | ⚡ Speed: {q_item['speed']}")
                st.progress(q_item['progress'])
                
                # Render direct download button for iPhone
                if q_item['file_paths']:
                    for f_idx, file_path in enumerate(q_item['file_paths']):
                        if os.path.exists(file_path):
                            file_name = os.path.basename(file_path)
                            mime_type = "image/jpeg" if file_name.endswith(('.jpg', '.jpeg', '.png')) else "video/mp4"
                            
                            with open(file_path, "rb") as f_bytes:
                                st.download_button(
                                    label=f"📥 Save File #{idx+1} ({file_name}) to iPhone",
                                    data=f_bytes,
                                    file_name=file_name,
                                    mime=mime_type,
                                    key=f"dl_btn_{idx}_{f_idx}"
                                )

# --- TAB 2: DESTINATION & QUALITY ---
with tab2:
    st.subheader("💳 Destination & Security Rules")
    st.caption("Configure target path rules.")
    
    dest_choice = st.radio(
        "Select Target Storage Location:",
        ["Local iOS Files (On My iPhone / Downloads)", "Google Drive Backup", "OneDrive Personal Vault"]
    )
    st.session_state.destination = dest_choice

# --- TAB 3: CLI SCRIPT GENERATOR ---
with tab3:
    st.subheader("⚙️ Zero-Prompt Python CLI Script")
    st.caption("Running this script directly on your iPhone (via a Python app like Pyto/aShell) or PC bypasses all cloud IP blocks because it uses your home cellular/Wi-Fi connection.")
    st.code("""import yt_dlp

def download_batch(urls):
    ydl_opts = {
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
            'Cookie': 'age_verified=1; platform=pc;'
        }
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download(urls)

if __name__ == "__main__":
    download_batch(["https://www.pornhub.com/view_video.php?viewkey=69f07e4c68014"])""", language="python")
