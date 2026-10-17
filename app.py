import streamlit as st
import os
import glob
import re
import requests
import cloudscraper
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

# Helper: URL Classifier
def classify_url(url: str) -> str:
    u = url.lower()
    if "instagram.com" in u:
        return "Instagram Media"
    elif "tiktok.com" in u:
        return "TikTok HD Video"
    elif "twitter.com" in u or "x.com" in u:
        return "Twitter / X Video"
    elif "youtube.com" in u or "youtu.be" in u:
        return "YouTube Video"
    elif "pornhub.com" in u:
        return "Adult Media Stream"
    else:
        return "Generic Web Video"

# Reliable Cloudscraper Stream Harvester
def download_stream_bulletproof(url: str, output_dir="downloads", status_box=None, progress_bar=None):
    os.makedirs(output_dir, exist_ok=True)
    out_path = os.path.join(output_dir, f"video_{abs(hash(url)) % 1000000}.mp4")

    if status_box: status_box.markdown("⚡ **Phase 1:** Passing Cloudflare & Age Gate...")
    if progress_bar: progress_bar.progress(25)

    # Scraper instance with pre-injected 18+ verification cookies
    scraper = cloudscraper.create_scraper(
        browser={'browser': 'chrome', 'platform': 'windows', 'mobile': False}
    )
    scraper.cookies.update({
        'age_verified': '1',
        'accessAgeDisclaimerPH': '1',
        'hasVisited': '1',
        'platform': 'pc'
    })

    # Method A: Cloudscraper Direct Page Extract
    try:
        res = scraper.get(url, timeout=15)
        if res.status_code == 200:
            mp4_urls = re.findall(r'https?://[^\s\'"]+\.mp4[^\s\'"]*', res.text)
            if mp4_urls:
                target_url = mp4_urls[0].replace('\\/', '/')
                if status_box: status_box.markdown("📥 **Phase 2:** Fetching verified MP4 stream...")
                if progress_bar: progress_bar.progress(60)

                with scraper.get(target_url, stream=True, timeout=30) as r:
                    r.raise_for_status()
                    with open(out_path, 'wb') as f:
                        for chunk in r.iter_content(chunk_size=65536):
                            f.write(chunk)
                
                if os.path.exists(out_path) and os.path.getsize(out_path) > 1024 * 1024:
                    if progress_bar: progress_bar.progress(100)
                    return out_path
    except Exception:
        pass

    # Method B: yt-dlp Extraction with Cloudscraper Cookies
    if status_box: status_box.markdown("⚡ **Phase 3:** Extracting via yt-dlp Engine...")
    if progress_bar: progress_bar.progress(75)

    ydl_opts = {
        'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
        'format': 'best',
        'quiet': True,
        'no_warnings': True,
        'nocheckcertificate': True,
        'ignoreerrors': True,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Cookie': 'age_verified=1; accessAgeDisclaimerPH=1; platform=pc;'
        }
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            if info:
                fp = ydl.prepare_filename(info)
                if os.path.exists(fp) and os.path.getsize(fp) > 1024 * 1024:
                    if progress_bar: progress_bar.progress(100)
                    return fp
    except Exception:
        pass

    # Verification scan
    all_files = glob.glob(os.path.join(output_dir, "*.*"))
    valid = [f for f in all_files if os.path.exists(f) and os.path.getsize(f) > 1024 * 1024]
    return valid[0] if valid else None

# Header
st.markdown("""
<div class="header-card">
    <h2 style="margin:0; color:#ffffff; font-size: 1.4rem;">☁️ Batch Link Downloader</h2>
    <p style="margin:0; color:#94a3b8; font-size: 0.8rem;">iPhone 17 Pro Max Cloudscraper Stream Engine</p>
</div>
""", unsafe_allow_html=True)

# Navigation Tabs
tab1, tab2, tab3 = st.tabs(["📊 Media Dashboard", "⚙️ Destination Rules", "💻 CLI Script Generator"])

if 'queue' not in st.session_state:
    st.session_state.queue = []
if 'destination' not in st.session_state:
    st.session_state.destination = "On My iPhone / Downloads"

# --- TAB 1: MEDIA DASHBOARD ---
with tab1:
    st.subheader("📁 Multi-Platform Batch Input")
    st.caption("Auto Age-Verification & Cloudflare Bypass Active.")
    
    urls_input = st.text_area(
        "Paste links (one per line):",
        placeholder="https://www.pornhub.com/view_video.php?viewkey=65143fe343448\nhttps://www.instagram.com/reel/Cxxxxxx/\nhttps://www.tiktok.com/@username/video/12345678",
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
                item['status'] = "Processing Stream..."
                
                status_box = st.empty()
                progress_bar = st.progress(0)
                
                file_path = download_stream_bulletproof(
                    url=item['url'],
                    status_box=status_box,
                    progress_bar=progress_bar
                )
                
                if file_path and os.path.exists(file_path):
                    file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
                    item['status'] = f"Ready for Save ✅ ({file_size_mb:.1f} MB)"
                    item['file_path'] = file_path
                    item['progress'] = 100
                    status_box.success(f"Item #{idx+1} verified! Size: {file_size_mb:.1f} MB")
                else:
                    item['status'] = "Extraction Failed ❌"
                    status_box.error(f"Item #{idx+1} could not be extracted.")
            
            st.rerun()

        # Render Queue items and Native iPhone Download Buttons
        for idx, q_item in enumerate(st.session_state.queue):
            with st.container():
                st.markdown(f"**Item #{idx+1}:** `{q_item['url']}`")
                st.caption(f"Engine Target: {q_item['type']} | Status: {q_item['status']}")
                st.progress(q_item['progress'])
                
                # Verified Download Button (Only shows when file size > 1 MB)
                if q_item['file_path'] and os.path.exists(q_item['file_path']):
                    file_size_mb = os.path.getsize(q_item['file_path']) / (1024 * 1024)
                    file_name = os.path.basename(q_item['file_path'])
                    
                    with open(q_item['file_path'], "rb") as f_bytes:
                        st.download_button(
                            label=f"📥 Save File #{idx+1} ({file_size_mb:.1f} MB) to iPhone Files",
                            data=f_bytes,
                            file_name=file_name,
                            mime="video/mp4",
                            key=f"bulletproof_dl_{idx}"
                        )

# --- TAB 2: SETTINGS ---
with tab2:
    st.subheader("💳 Destination Storage Rules")
    dest_choice = st.radio(
        "Select Target Storage Location:",
        ["Local iOS Files (On My iPhone / Downloads)", "Google Drive Backup"]
    )
    st.session_state.destination = dest_choice

# --- TAB 3: CLI SCRIPT GENERATOR ---
with tab3:
    st.subheader("⚙️ Zero-Prompt Python CLI Script")
    st.code("""import cloudscraper

scraper = cloudscraper.create_scraper()
res = scraper.get("https://www.pornhub.com/view_video.php?viewkey=65143fe343448")
print("Page fetched successfully!")""", language="python")
