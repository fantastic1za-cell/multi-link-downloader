import streamlit as st
import os
import time
from batch_downloader import BatchDownloader

# Page configuration
st.set_page_config(
    page_title="Batch Link Downloader",
    page_icon="☁️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Dark glassmorphism custom CSS styling
st.markdown("""
<style>
    .stApp { background-color: #0b1120; color: #f8fafc; }
    .header-card { background: rgba(30, 41, 59, 0.7); padding: 18px; border-radius: 16px; border: 1px solid rgba(255, 255, 255, 0.08); margin-bottom: 20px; }
    .stButton>button { background-color: #0284c7; color: white; border-radius: 12px; border: none; font-weight: 600; padding: 10px 20px; width: 100%; }
    .stButton>button:hover { background-color: #0369a1; }
</style>
""", unsafe_allow_html=True)

# Header Section
st.markdown("""
<div class="header-card">
    <h2 style="margin:0; color:#ffffff; font-size: 1.4rem;">☁️ Batch Link Downloader</h2>
    <p style="margin:0; color:#94a3b8; font-size: 0.8rem;">iPhone 17 Pro Max Multi-Source Media Hub</p>
</div>
""", unsafe_allow_html=True)

# Navigation Tabs
tab1, tab2, tab3 = st.tabs(["📊 Media Dashboard", "⚙️ Destination & Quality", "💻 CLI Script Generator"])

# Session State Initializations
if 'queue' not in st.session_state:
    st.session_state.queue = []
if 'destination' not in st.session_state:
    st.session_state.destination = "On My iPhone / Downloads"

downloader = BatchDownloader()

# --- TAB 1: MEDIA DASHBOARD ---
with tab1:
    st.subheader("📁 Multi-Platform Batch Input")
    st.caption("Supports YouTube, Twitter/X, Instagram Photos/Profiles/Reels & Generic Web Video Links.")
    
    urls_input = st.text_area(
        "Paste links (one per line):",
        placeholder="https://www.instagram.com/p/Cxxxxxx/ (Instagram Photo/Post)\nhttps://x.com/username/status/12345678 (Twitter/X Video)\nhttps://www.youtube.com/watch?v=xxxxxx (YouTube Video)\nhttps://www.vimeo.com/xxxxxx (Web Link Video)",
        height=150
    )
    
    st.info(f"📂 Active Destination: `{st.session_state.destination}`")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("▶️ Process & Add to Queue"):
            if urls_input.strip():
                lines = [line.strip() for line in urls_input.split('\n') if line.strip()]
                st.session_state.queue = []
                for url in lines:
                    media_type = downloader.classify_url(url)
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

                try:
                    files = downloader.download_url(item['url'], progress_callback=update_progress)
                    if files:
                        item['status'] = "Completed ✅"
                        item['file_paths'] = files
                        item['progress'] = 100
                        item['speed'] = "0.0 MB/s"
                        status_box.success(f"Item #{idx+1} Downloaded successfully ({len(files)} file(s))!")
                    else:
                        item['status'] = "Error / Restricted ❌"
                except Exception as e:
                    item['status'] = f"Failed: {str(e)}"
                    status_box.error(f"Error downloading item #{idx+1}: {e}")
            
            st.success("🎉 Multi-platform batch processing complete!")
            st.rerun()

        # Display Queue items and File Download buttons
        for idx, q_item in enumerate(st.session_state.queue):
            with st.container():
                st.markdown(f"**Item #{idx+1}:** `{q_item['url']}`")
                st.caption(f"Engine Target: {q_item['type']} | Status: {q_item['status']} | ⚡ Speed: {q_item['speed']}")
                st.progress(q_item['progress'])
                
                # Render direct save button for each downloaded photo/video file
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
    st.caption("Configure local storage paths and zero-prompt backup integrations.")
    
    dest_choice = st.radio(
        "Select Target Storage Location:",
        ["Local iOS Files (On My iPhone / Downloads)", "Google Drive Backup (Privacy Screen)", "OneDrive Personal Vault (Face ID Lock)"]
    )
    st.session_state.destination = dest_choice
    
    st.subheader("🎬 Video & Image Quality Settings")
    quality = st.selectbox("Maximum Resolution Filter:", ["Highest Available (1080p/4K/Original)", "720p HD (Fast Download)", "Audio Only (MP3)"])

# --- TAB 3: CLI SCRIPT GENERATOR ---
with tab3:
    st.subheader("⚙️ Zero-Prompt Python CLI Script")
    st.caption("Generates `batch_downloader.py` for direct command line batch execution on iOS or PC.")
    
    cli_code = """import os
import yt_dlp
import instaloader

def download_batch(url_list):
    # Initializes multi-engine batch script
    downloader = BatchDownloader()
    for url in url_list:
        downloader.download_url(url)

if __name__ == "__main__":
    urls = [
        "https://www.instagram.com/p/Cxxxxxx/",
        "https://x.com/username/status/12345678",
        "https://www.youtube.com/watch?v=xxxxxx"
    ]
    download_batch(urls)
"""
    st.code(cli_code, language="python")
