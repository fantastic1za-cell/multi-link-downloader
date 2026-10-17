import os
import streamlit as st
from batch_downloader import BatchDownloader

st.set_page_config(
    page_title="Batch Media Downloader",
    page_icon="📥",
    layout="wide"
)

st.title("📥 Batch Link Downloader Dashboard")
st.markdown("Paste multiple video links or Instagram profile URLs below to batch-download highest quality files directly to your device.")

# Sidebar Configuration
st.sidebar.header("⚙️ Destination Settings")
default_path = os.path.abspath(os.path.join(os.path.expanduser("~"), "Downloads", "BatchDownloads"))

download_folder = st.sidebar.text_input(
    "Save Location Folder:",
    value=default_path,
    help="You can specify a local path, or your Google Drive / OneDrive synced folder path."
)

st.sidebar.markdown("""
---
### 📁 Folder Organization Rules
- **Instagram Profiles**: Auto-saved into `Instagram/[username]/`
- **Instagram Reels/Posts**: Saved into `Instagram/Media/`
- **Other Video Sites**: Saved into `Videos/`
""")

# Input section
links_input = st.text_area(
    "Paste Links (One URL per line):",
    height=220,
    placeholder="https://www.instagram.com/username/\nhttps://www.instagram.com/reel/Cxxxxxx/\nhttps://www.youtube.com/watch?v=xxxxxx\nhttps://vimeo.com/xxxxxx"
)

col1, col2 = st.columns([1, 4])
with col1:
    start_btn = st.button("🚀 Start Batch Download", type="primary", use_container_width=True)

if start_btn:
    urls = [line.strip() for line in links_input.splitlines() if line.strip()]
    
    if not urls:
        st.warning("Please paste at least one valid URL.")
    else:
        downloader = BatchDownloader(output_dir=download_folder)
        
        st.info(f"Downloading {len(urls)} target link(s) to: `{download_folder}`")
        
        progress_bar = st.progress(0)
        status_box = st.empty()
        log_container = st.container()

        success_count = 0
        failed_count = 0

        for idx, url in enumerate(urls):
            status_box.text(f"[{idx+1}/{len(urls)}] Processing: {url}")
            
            def log_callback(msg):
                status_box.text(f"[{idx+1}/{len(urls)}] {msg}")

            success, message = downloader.download_media_link(url, status_callback=log_callback)
            
            with log_container:
                if success:
                    st.success(message)
                    success_count += 1
                else:
                    st.error(message)
                    failed_count += 1

            progress_bar.progress((idx + 1) / len(urls))

        status_box.empty()
        st.balloons()
        st.success(f"🎉 Batch operation complete! Success: {success_count} | Failed: {failed_count}")
        st.info(f"All files have been saved to: `{download_folder}`")
