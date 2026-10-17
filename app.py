import streamlit as st
import requests
import re
import os
import urllib.parse

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

# Clean and preserve original source titles
def clean_filename(name: str) -> str:
    clean = re.sub(r'[^a-zA-Z0-9_\-\s]', '', name).strip().replace(' ', '_')
    return f"{clean}.mp4" if clean else "downloaded_media.mp4"

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

# High-Precision Multi-Tier Media Extractor & Validator
def resolve_and_fetch_media(url: str, status_box, progress_bar):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Cookie': 'age_verified=1; accessAgeDisclaimerPH=1; hasVisited=1; platform=pc;',
        'Referer': 'https://www.google.com/'
    }

    status_box.markdown("🔍 **Step 1/3:** Bypassing Cloud IP restrictions & querying API nodes...")
    progress_bar.progress(20)

    candidate_urls = []
    title_name = f"source_media_{abs(hash(url)) % 1000000}"

    # Tier 1: Query API Relay Matrix for 4K/HD Direct MP4 Streams
    api_nodes = [
        "https://api.cobalt.tools/api/json",
        "https://cobalt-api.kwiatek.xyz/api/json"
    ]
    
    for endpoint in api_nodes:
        try:
            payload = {"url": url, "videoQuality": "max"}
            req_headers = {"Accept": "application/json", "Content-Type": "application/json"}
            res = requests.post(endpoint, json=payload, headers=req_headers, timeout=8)
            if res.status_code == 200:
                data = res.json()
                if data.get("url"):
                    candidate_urls.append(data.get("url"))
                if data.get("filename"):
                    title_name = data.get("filename").replace('.mp4', '')
                break
        except Exception:
            continue

    # Tier 2: Direct Page Source Parsing for Uncompressed Stream Containers
    status_box.markdown("🌐 **Step 2/3:** Extracting full-length media streams...")
    progress_bar.progress(50)
    try:
        page_res = requests.get(url, headers=headers, timeout=10)
        if page_res.status_code == 200:
            # Extract source video title
            t_match = re.search(r'<title>(.*?)</title>', page_res.text, re.IGNORECASE)
            if t_match and title_name.startswith("source_media_"):
                title_name = t_match.group(1).replace('- Pornhub.com', '').replace('Watch', '').strip()

            # Find direct MP4 stream links
            mp4_matches = re.findall(r'https?://[^\s\'"]+\.mp4[^\s\'"]*', page_res.text)
            for m in mp4_matches:
                clean_m = m.replace('\\/', '/')
                if clean_m not in candidate_urls:
                    candidate_urls.append(clean_m)
    except Exception:
        pass

    if not candidate_urls:
        candidate_urls.append(url)

    # Tier 3: Fetch & Validate Full Video Binary Bytes (> 5 MB Threshold)
    status_box.markdown("📥 **Step 3/3:** Streaming binary video bytes into session memory...")
    progress_bar.progress(75)

    for target_url in candidate_urls:
        try:
            download_endpoint = target_url if target_url.startswith("http") else f"https://corsproxy.io/?{urllib.parse.quote(target_url)}"
            with requests.get(download_endpoint, headers=headers, stream=True, timeout=35) as video_res:
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

                    # Strict size check: Must be > 5 MB to prevent serving small HTML error pages or 1.5 MB previews
                    if len(binary_buffer) > 5 * 1024 * 1024:
                        progress_bar.progress(100)
                        return bytes(binary_buffer), clean_filename(title_name)
        except Exception:
            continue

    progress_bar.progress(0)
    return None, None

# Header
st.markdown("""
<div class="header-card">
    <h2 style="margin:0; color:#ffffff; font-size: 1.4rem;">☁️ Batch Link Downloader</h2>
    <p style="margin:0; color:#94a3b8; font-size: 0.8rem;">iPhone 17 Pro Max 4K Fail-Safe Media Hub</p>
</div>
""", unsafe_allow_html=True)

# Session state initialization
if 'queue' not in st.session_state:
    st.session_state.queue = []
if 'destination' not in st.session_state:
    st.session_state.destination = "On My iPhone / Downloads"

# Navigation Tabs
tab1, tab2, tab3 = st.tabs(["📊 Media Dashboard", "⚙️ Destination Rules", "💻 CLI Script Generator"])

# --- TAB 1: MEDIA DASHBOARD ---
with tab1:
    st.subheader("📁 Multi-Platform Batch Input (Max Quality)")
    st.caption("Supports YouTube, TikTok, Instagram, Twitter/X, Adult Media & Web Videos.")
    
    urls_input = st.text_area(
        "Paste links (one per line):",
        placeholder="https://www.pornhub.com/view_video.php?viewkey=69f07e4c68014\nhttps://www.instagram.com/reel/Cxxxxxx/\nhttps://www.tiktok.com/@username/video/12345678",
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
                item['status'] = "Processing Stream..."
                
                status_box = st.empty()
                progress_bar = st.progress(0)
                
                binary_bytes, fname = resolve_and_fetch_media(
                    url=item['url'],
                    status_box=status_box,
                    progress_bar=progress_bar
                )
                
                if binary_bytes and len(binary_bytes) > 5 * 1024 * 1024:
                    file_size_mb = len(binary_bytes) / (1024 * 1024)
                    item['status'] = f"Ready for Save ✅ ({file_size_mb:.1f} MB)"
                    item['binary_data'] = binary_bytes
                    item['file_name'] = fname
                    item['progress'] = 100
                    status_box.success(f"Item #{idx+1} verified! Title: {fname} | Size: {file_size_mb:.1f} MB")
                else:
                    item['status'] = "Extraction Error ❌"
                    status_box.error(f"Item #{idx+1} could not be extracted.")
            
            st.rerun()

        # Render Native Save Buttons for iOS Safari
        for idx, q_item in enumerate(st.session_state.queue):
            with st.container():
                st.markdown(f"**Item #{idx+1}:** `{q_item['url']}`")
                st.caption(f"Engine Target: {q_item['type']} | Status: {q_item['status']}")
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
    st.code("""import requests

def download_video(url):
    headers = {'Cookie': 'age_verified=1; accessAgeDisclaimerPH=1; platform=pc;'}
    res = requests.get(url, headers=headers, stream=True)
    with open("video.mp4", "wb") as f:
        for chunk in res.iter_content(chunk_size=65536):
            f.write(chunk)

download_video("https://www.pornhub.com/view_video.php?viewkey=69f07e4c68014")""", language="python")
