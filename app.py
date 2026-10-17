import streamlit as st
import time
import os
from batch_downloader import BatchDownloader

# Page configuration
st.set_page_config(
    page_title="Batch Link Downloader",
    page_icon="☁️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom Styling matching dark glassmorphism layout
st.markdown("""
<style>
    .stApp { background-color: #0b1120; color: #f8fafc; }
    .header-card { background: rgba(30, 41, 59, 0.7); padding: 18px; border-radius: 16px; border: 1px solid rgba(255, 255, 255, 0.08); margin-bottom: 20px; }
    .stButton>button { background-color: #0284c7; color: white; border-radius: 12px; border: none; font-weight: 600; padding: 10px 20px; width: 100%; }
    .stButton>button:hover { background-color: #0369a1; }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="header-card">
    <h2 style="margin:0; color:#ffffff; font-size: 1.4rem;">☁️ Batch Link Downloader</h2>
    <p style="margin:0; color:#94a3b8; font-size: 0.8rem;">iPhone 17 Pro Max Automated Media Hub</p>
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
    st.subheader("📁 Batch Link Input")
    st.caption("Paste links below. Instagram profiles, Reels, and generic video links are auto-classified.")
    
    urls_input = st.text_area(
        "Paste links (one per line):",
        placeholder="https://www.instagram.com/reel/C3x9L0xO8P/\nhttps://www.youtube.com/watch?v=xxxxxx",
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
                    media_type = "Instagram Reel/Post" if "instagram.com" in url else "Generic Video Stream"
                    st.session_state.queue.append({
                        "url": url,
                        "type": media_type,
                        "status": "Pending",
                        "progress": 0,
                        "speed": "0.0 MB/s",
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
                item['status'] = "Downloading..."
                
                status_box = st.empty()
                progress_bar = st.progress(0)
                
                def update_progress(percent, speed_mb):
                    item['progress'] = int(percent)
                    item['speed'] = f"{speed_mb:.1f} MB/s"
                    status_box.markdown(f"**Item #{idx+1}:** Downloading `{item['url']}` | ⚡ Speed: **{item['speed']}**")
                    progress_bar.progress(int(percent))

                try:
                    filepath = downloader.download_url(item['url'], progress_callback=update_progress)
                    if filepath and os.path.exists(filepath):
                        item['status'] = "Completed ✅"
                        item['file_path'] = filepath
                        item['progress'] = 100
                        item['speed'] = "0.0 MB/s"
                        status_box.success(f"Item #{idx+1} Downloaded successfully!")
                    else:
                        item['status'] = "Error / Restricted ❌"
                except Exception as e:
                    item['status'] = f"Failed: {str(e)}"
                    status_box.error(f"Error downloading item #{idx+1}: {e}")
            
            st.success("🎉 Batch processing complete!")
            st.rerun()

        # Display Queue items and File Download buttons
        for idx, q_item in enumerate(st.session_state.queue):
            with st.container():
                st.markdown(f"**Item #{idx+1}:** `{q_item['url']}`")
                st.caption(f"Type: {q_item['type']} | Status: {q_item['status']} | ⚡ Speed: {q_item['speed']}")
                st.progress(q_item['progress'])
                
                # Show Save to iPhone Button when File Path exists
                if q_item['file_path'] and os.path.exists(q_item['file_path']):
                    with open(q_item['file_path'], "rb") as file_bytes:
                        st.download_button(
                            label=f"📥 Save File #{idx+1} to iPhone",
                            data=file_bytes,
                            file_name=os.path.basename(q_item['file_path']),
                            mime="video/mp4",
                            key=f"dl_btn_{idx}"
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
    
    st.subheader("🎬 Video Quality Settings")
    quality = st.selectbox("Maximum Resolution Filter:", ["Highest Available (1080p/4K)", "720p HD (Fast Download)", "Audio Only (MP3)"])

# --- TAB 3: CLI SCRIPT GENERATOR ---
with tab3:
    st.subheader("⚙️ Zero-Prompt Python CLI Script")
    st.caption("Generates `batch_downloader.py` for direct command line batch execution on iOS or PC.")
    
    cli_code = """import os
import yt_dlp

def download_batch(url_list):
    ydl_opts = {'outtmpl': 'downloads/%(title)s.%(ext)s'}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download(url_list)

if __name__ == "__main__":
    urls = ["https://www.instagram.com/reel/C3x9L0xO8P/"]
    download_batch(urls)
"""
    st.code(cli_code, language="python")
