import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Batch Link Downloader Dashboard",
    page_icon="📥",
    layout="wide",
    initial_sidebar_state="collapsed"
)

html_code = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Batch Link Downloader Dashboard</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        body { background-color: #0f172a; color: #f8fafc; font-family: system-ui, -apple-system, sans-serif; }
        .glass { background: rgba(30, 41, 59, 0.7); backdrop-filter: blur(12px); border: 1px solid rgba(255, 255, 255, 0.1); }
    </style>
</head>
<body class="p-4 md:p-8 min-h-screen">
    <div class="max-w-4xl mx-auto space-y-6">
        <!-- Header -->
        <div class="glass rounded-2xl p-6 flex items-center justify-between shadow-2xl">
            <div class="flex items-center space-x-4">
                <div class="bg-indigo-600 p-3 rounded-xl shadow-lg">
                    <i class="fa-solid fa-cloud-arrow-down text-2xl text-white"></i>
                </div>
                <div>
                    <h1 class="text-xl font-bold text-white">Batch Link Downloader</h1>
                    <p class="text-xs text-slate-400">Automated Media Classifier & Extractor</p>
                </div>
            </div>
            <span class="bg-emerald-500/10 text-emerald-400 text-xs px-3 py-1 rounded-full border border-emerald-500/20 flex items-center gap-2">
                <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span> Ready
            </span>
        </div>

        <!-- Input Area -->
        <div class="glass rounded-2xl p-6 space-y-4">
            <label class="block text-sm font-semibold text-slate-300">Paste Links (One per line)</label>
            <textarea id="linkInput" rows="5" class="w-full bg-slate-900/80 border border-slate-700 rounded-xl p-4 text-sm text-slate-200 focus:outline-none focus:border-indigo-500 placeholder-slate-500 transition-all" placeholder="https://www.instagram.com/username/&#10;https://www.instagram.com/reel/Cxxxxxx/&#10;https://www.youtube.com/watch?v=xxxxxx"></textarea>
            
            <div class="flex flex-col sm:flex-row justify-between items-center gap-4 pt-2">
                <div class="text-xs text-slate-400 flex items-center gap-2">
                    <i class="fa-solid fa-folder-tree text-indigo-400"></i> Saves to: <span class="text-slate-200 font-mono bg-slate-800 px-2 py-0.5 rounded">On My iPhone / Downloads</span>
                </div>
                <button onclick="processLinks()" class="w-full sm:w-auto bg-indigo-600 hover:bg-indigo-500 text-white font-semibold px-6 py-2.5 rounded-xl transition-all shadow-lg shadow-indigo-600/30 flex items-center justify-center gap-2">
                    <i class="fa-solid fa-rocket"></i> Start Batch Download
                </button>
            </div>
        </div>

        <!-- Queue Status -->
        <div id="queueContainer" class="glass rounded-2xl p-6 space-y-4 hidden">
            <h2 class="text-sm font-semibold text-slate-300 flex items-center justify-between">
                <span>Download Queue</span>
                <span id="queueCount" class="text-xs text-indigo-400">0 Items</span>
            </h2>
            <div id="queueList" class="space-y-3"></div>
        </div>
    </div>

    <script>
        function processLinks() {
            const input = document.getElementById('linkInput').value.trim();
            if (!input) return;

            const links = input.split('\\n').filter(l => l.trim() !== '');
            const queueContainer = document.getElementById('queueContainer');
            const queueList = document.getElementById('queueList');
            const queueCount = document.getElementById('queueCount');

            queueList.innerHTML = '';
            queueCount.innerText = `${links.length} Items`;
            queueContainer.classList.remove('hidden');

            links.forEach((link, idx) => {
                let type = 'Generic Video';
                let folder = 'Videos/';
                let icon = 'fa-video';

                if (link.includes('instagram.com')) {
                    if (link.includes('/reel/') || link.includes('/p/')) {
                        type = 'Instagram Reel/Post';
                        folder = 'Instagram/Media/';
                        icon = 'fa-instagram';
                    } else {
                        type = 'Instagram Profile';
                        folder = 'Instagram/[Profile]/';
                        icon = 'fa-user';
                    }
                }

                const item = document.createElement('div');
                item.className = 'bg-slate-900/60 border border-slate-800 p-4 rounded-xl flex items-center justify-between gap-4';
                item.innerHTML = `
                    <div class="flex items-center gap-3 overflow-hidden">
                        <i class="fa-brands ${icon} text-indigo-400 text-lg"></i>
                        <div class="truncate">
                            <p class="text-xs font-mono text-slate-300 truncate">${link}</p>
                            <p class="text-[10px] text-slate-500">${type} &bull; Destination: ${folder}</p>
                        </div>
                    </div>
                    <span class="text-xs bg-indigo-500/10 text-indigo-400 px-2.5 py-1 rounded-md border border-indigo-500/20 whitespace-nowrap">Processing...</span>
                `;
                queueList.appendChild(item);
            });
        }
    </script>
</body>
</html>
"""

components.html(html_code, height=750, scrolling=True)
