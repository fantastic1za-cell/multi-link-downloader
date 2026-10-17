import streamlit as st
import requests
import re
import os

# Page configuration
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
</style>
""", unsafe_allow_html=True)

# Clean and preserve source file title
def clean_filename(name: str) -> str:
    clean = re.sub(r'[^a-zA-Z0-9_\-\s]', '', name).strip().replace(' ', '_')
    return f"{clean}.mp4" if clean else "downloaded_media.mp4"

# Master File Downloader & Proxy Relay
def resolve_and_fetch_binary(url: str, status_box, progress_bar):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'Accept': '*/*',
        'Cookie': 'age_verified=1; accessAgeDisclaimerPH=1; hasVisited=1; platform=pc;'
    }

    status_box.markdown("🔍 **Step 1/3:** Bypassing Cloud IP Restrictions...")
    progress_bar.progress(25)

    stream_url = None
    title_name = f"video_{abs(hash(url)) % 1000000}"

    # Tier 1: Query API Relay Engine for Uncompressed Video Direct Stream
    try:
        cobalt_payload = {"url": url, "videoQuality": "max"}
        cobalt_headers = {"Accept": "application/json", "Content-Type": "application/json"}
        api_res = requests.post("https://api.cobalt.tools/api/json", json=cobalt_payload, headers=cobalt_headers, timeout=10)
        if api_res.status_code == 200:
            data = api_res.json()
            if data.get("url"):
                stream_url = data.get("url")
            if data.get("filename"):
                title_name = data.get("filename").replace('.mp4', '')
    except Exception:
        pass

    # Tier 2: Public Proxy Fallback
    if not stream_url:
        status_box.markdown("🌐 **Step 2/3:** Harvesting Binary Stream through Proxy Relay...")
        progress_bar.progress(50)
        try:
            proxy_url = f"https://corsproxy.io/?{requests.utils.quote(url)}"
            res = requests.get(proxy_url, headers=headers, timeout=12)
            if res.status_code == 200:
                mp4_matches = re.findall(r'https?://[^\s\'"]+\.mp4[^\s\'"]*', res.text)
                if mp4_matches:
                    stream_url = mp4_matches[0].replace('\\/', '/')
        except Exception:
            pass

    if not stream_url:
        stream_url = url

    # Tier 3: Fetch Direct Binary Bytes to Session Storage
    status_box.markdown("📥 **Step 3/3:** Downloading Binary File to Buffer...")
    progress_bar.progress(75)

    try:
        download_target = stream_url if stream_url.startswith("http") else f"https://corsproxy.io/?{requests.utils.quote(stream_url)}"
        with requests.get(download_target, headers=headers, stream=True, timeout=35) as video_res:
            if video_res.status_code == 200:
                content_length = int(video_res.headers.get('content-length', 0))
                downloaded = 0
                binary_buffer = bytearray()

                for chunk in video_res.iter_content(chunk_size=65536):
                    if chunk:
                        binary_buffer.extend(chunk)
                        downloaded += len(chunk)
                        if content_length > 0:
                            p = int((downloaded / content_length) * 100)
                            progress_bar.progress(min(p, 99))

                # Verify file size > 500 KB to avoid serving truncated error pages
                if len(binary_buffer) > 500 * 1024:
                    progress_bar.progress(100)
                    return bytes(binary_buffer), clean_filename(title_name)
    except Exception:
        pass

    progress_bar.progress(0)
    return None, None

# Header Section
st.markdown("""
<div class="header-card">
    <h2 style="margin:0; color:#ffffff; font-size: 1.4rem;">☁️ Batch Link Downloader</h2>
    <p style="margin:0; color:#94a3b8; font-size: 0.8rem;">iPhone Direct Binary File Download Engine</p>
</div>
""", unsafe_allow_html=True)

# Session state initialization
if 'queue' not in st.session_state:
    st.session_state.queue = []

# Media Input Dashboard
st.subheader("📁 Multi-Platform Batch Input")
urls_input = st.text_area(
    "Paste links (one per line):",
    placeholder="https://www.pornhub.com/view_video.php?viewkey=69f07e4c68014\nhttps://www.instagram.com/reel/Cxxxxxx/\nhttps://www.tiktok.com/@username/video/12345678",
    height=140
)

st.info("📂 Target Destination: `On My iPhone / Downloads`")

col1, col2 = st.columns(2)
with col1:
    if st.button("▶️ Process & Add to Queue"):
        if urls_input.strip():
            lines = [line.strip() for line in urls_input.split('\n') if line.strip()]
            st.session_state.queue = []
            for url in lines:
                st.session_state.queue.append({
                    "url": url,
                    "status": "Pending",
                    "progress": 0,
                    "binary_data": None,
                    "file_name": None
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
            item['status'] = "Downloading Binary File..."
            
            status_box = st.empty()
            progress_bar = st.progress(0)
            
            binary_bytes, fname = resolve_and_fetch_binary(
                url=item['url'],
                status_box=status_box,
                progress_bar=progress_bar
            )
            
            if binary_bytes and len(binary_bytes) > 500 * 1024:
                file_size_mb = len(binary_bytes) / (1024 * 1024)
                item['status'] = f"Ready for Save ✅ ({file_size_mb:.1f} MB)"
                item['binary_data'] = binary_bytes
                item['file_name'] = fname
                item['progress'] = 100
                status_box.success(f"Item #{idx+1} complete! File Size: {file_size_mb:.1f} MB")
            else:
                item['status'] = "Extraction Error ❌"
                status_box.error(f"Item #{idx+1} could not be downloaded.")
        
        st.rerun()

    # Render Native Streamlit Save Buttons for Direct iOS File Downloads
    for idx, q_item in enumerate(st.session_state.queue):
        with st.container():
            st.markdown(f"**Item #{idx+1}:** `{q_item['url']}`")
            st.caption(f"Status: {q_item['status']}")
            st.progress(q_item['progress'])
            
            if q_item['binary_data'] is not None:
                size_mb = len(q_item['binary_data']) / (1024 * 1024)
                st.download_button(
                    label=f"📥 Download File \"{q_item['file_name']}\" ({size_mb:.1f} MB) to iPhone",
                    data=q_item['binary_data'],
                    file_name=q_item['file_name'],
                    mime="video/mp4",
                    key=f"dl_native_btn_{idx}"
                )
