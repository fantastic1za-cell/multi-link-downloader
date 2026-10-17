import streamlit as st
import requests
import re
import os
import time

# Page Configuration
st.set_page_config(
    page_title="Batch Link Downloader",
    page_icon="☁️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Dark Glassmorphism Styling
st.markdown("""
<style>
    .stApp { background-color: #0b1120; color: #f8fafc; }
    .header-card { background: rgba(30, 41, 59, 0.7); padding: 18px; border-radius: 16px; border: 1px solid rgba(255, 255, 255, 0.08); margin-bottom: 20px; }
    .stButton>button { background-color: #0284c7; color: white; border-radius: 12px; border: none; font-weight: 600; padding: 10px 20px; width: 100%; }
    .stButton>button:hover { background-color: #0369a1; }
    .item-card { background: rgba(15, 23, 42, 0.6); border: 1px solid rgba(51, 65, 85, 0.6); padding: 16px; border-radius: 12px; margin-bottom: 12px; }
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

# Multi-Tier Failsafe Media Resolver
def resolve_and_fetch_binary(url: str, status_box, progress_bar):
    headers = {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.9',
    }

    status_box.markdown("🔍 **Step 1/3:** Resolving video stream headers...")
    progress_bar.progress(25)

    stream_url = None

    # Tier 1: Direct Cobalt Media API Bridge
    try:
        api_payload = {"url": url, "videoQuality": "max"}
        api_headers = {"Accept": "application/json", "Content-Type": "application/json"}
        response = requests.post("https://api.cobalt.tools/api/json", json=api_payload, headers=api_headers, timeout=8)
        if response.status_code == 200:
            data = response.json()
            if data.get("status") in ["redirect", "stream", "picker"]:
                stream_url = data.get("url")
    except Exception:
        pass

    # Tier 2: Public Proxy Gateway Fallback
    if not stream_url:
        status_box.markdown("🌐 **Step 2/3:** Bypassing datacenter restrictions via Proxy Gateway...")
        progress_bar.progress(50)
        gateways = [
            f"https://corsproxy.io/?{requests.utils.quote(url)}",
            f"https://api.allorigins.win/raw?url={requests.utils.quote(url)}"
        ]
        for gw in gateways:
            try:
                res = requests.get(gw, headers=headers, timeout=10)
                if res.status_code == 200:
                    mp4_matches = re.findall(r'https?://[^\s\'"]+\.mp4[^\s\'"]*', res.text)
                    if mp4_matches:
                        stream_url = mp4_matches[0].replace('\\/', '/')
                        break
            except Exception:
                continue

    # Tier 3: Direct Stream Target
    if not stream_url:
        stream_url = url

    # Binary Fetching for Native iOS Delivery
    status_box.markdown("📥 **Step 3/3:** Downloading binary bytes into device session buffer...")
    progress_bar.progress(75)

    try:
        # Fetch target stream via proxy to ensure datacenter bypass
        target = f"https://corsproxy.io/?{requests.utils.quote(stream_url)}" if not stream_url.startswith("https://corsproxy.io") else stream_url
        res = requests.get(target, headers=headers, stream=True, timeout=25)
        
        if res.status_code == 200:
            content_length = int(res.headers.get('content-length', 0))
            downloaded = 0
            binary_data = bytearray()
            
            for chunk in res.iter_content(chunk_size=65536):
                if chunk:
                    binary_data.extend(chunk)
                    downloaded += len(chunk)
                    if content_length > 0:
                        p = int((downloaded / content_length) * 100)
                        progress_bar.progress(min(p, 99))
            
            if len(binary_data) > 1024:
                progress_bar.progress(100)
                return bytes(binary_data)
    except Exception:
        pass

    progress_bar.progress(0)
    return None

# Header Section
st.markdown("""
<div class="header-card">
    <h2 style="margin:0; color:#ffffff; font-size: 1.4rem;">☁️ Batch Link Downloader</h2>
    <p style="margin:0; color:#94a3b8; font-size: 0.8rem;">iPhone 17 Pro Max Direct iOS File Delivery Hub</p>
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
    st.subheader("📁 Multi-Platform Batch Input")
    st.caption("Supports YouTube, Twitter/X, Instagram, Adult Media & Generic Web Video Links.")
    
    urls_input = st.text_area(
        "Paste links (one per line):",
        placeholder="https://www.pornhub.com/view_video.php?viewkey=69f07e4c68014\nhttps://www.instagram.com/reel/Cxxxxxx/\nhttps://x.com/username/status/12345678",
        height=140
    )
    
    st.info(f"📂 Active Storage Target: `{st.session_state.destination}`")
    
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
                        "binary_data": None
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
                item['status'] = "Processing Failsafe Pipeline..."
                
                status_box = st.empty()
                progress_bar = st.progress(0)
                
                binary_output = resolve_and_fetch_binary(
                    url=item['url'],
                    status_box=status_box,
                    progress_bar=progress_bar
                )
                
                if binary_output:
                    item['status'] = "Ready for Save ✅"
                    item['binary_data'] = binary_output
                    item['progress'] = 100
                    status_box.success(f"Item #{idx+1} successfully compiled for iOS save!")
                else:
                    item['status'] = "Stream Extraction Failed ❌"
                    status_box.error(f"Item #{idx+1} stream could not be fetched.")
            
            st.rerun()

        # Render Queue items and Native iPhone Download Buttons
        for idx, q_item in enumerate(st.session_state.queue):
            with st.container():
                st.markdown(f"**Item #{idx+1}:** `{q_item['url']}`")
                st.caption(f"Engine Target: {q_item['type']} | Status: {q_item['status']}")
                st.progress(q_item['progress'])
                
                # Native Binary File Exporter for iOS Safari
                if q_item['binary_data'] is not None:
                    file_name = f"media_file_{idx+1}.mp4"
                    st.download_button(
                        label=f"📥 Download File #{idx+1} ({file_name}) to iPhone Files",
                        data=q_item['binary_data'],
                        file_name=file_name,
                        mime="video/mp4",
                        key=f"native_dl_btn_{idx}"
                    )

# --- TAB 2: DESTINATION RULES ---
with tab2:
    st.subheader("💳 Storage Path Configuration")
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
    ydl_opts = {'outtmpl': 'downloads/%(title)s.%(ext)s'}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download(urls)

download(["https://x.com/status/123456"])""", language="python")
