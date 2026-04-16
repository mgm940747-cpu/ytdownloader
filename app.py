import streamlit as st
import yt_dlp
import subprocess
import os
import random

# Page Config
st.set_page_config(page_title="Pro Movie Downloader", page_icon="🎬", layout="wide")

# --- Custom Theme & Eye-Comfort CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #F8FAFC; }
    h1 { color: #1E293B !important; font-weight: 800 !important; }
    div.stButton > button:first-child { background-color: #334155; color: white; border: none; border-radius: 8px; height: 3rem; transition: all 0.3s ease; }
    div.stButton > button:first-child:hover { background-color: #0F172A; color: white; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
    section[data-testid="stSidebar"] { background-color: #1E293B !important; }
    section[data-testid="stSidebar"] .stMarkdown, section[data-testid="stSidebar"] p { color: #E2E8F0 !important; }
    div[data-testid="stExpander"], .stContainer { border-radius: 12px !important; border: 1px solid #E2E8F0 !important; background-color: white !important; padding: 10px; }
    .landing-container { display: flex; flex-direction: column; align-items: center; justify-content: center; height: 60vh; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# --- Functions ---
def update_library():
    try:
        subprocess.check_call(["pip", "install", "--upgrade", "yt-dlp"])
        return "✅ Engine updated to latest version!"
    except:
        return "❌ Update failed."

def fetch_filtered_video(query):
    # 403 Error ရှောင်ရန် User-Agent ထည့်ခြင်း
    ydl_opts = {
        'quiet': True,
        'match_filter': yt_dlp.utils.match_filter_func('duration > 300 & duration < 900'),
        'extract_flat': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            search_results = ydl.extract_info(f"ytsearch10:{query} movie recap", download=False)
            entries = search_results.get('entries', [])
            if entries:
                selected = random.choice(entries)
                return f"https://www.youtube.com/watch?v={selected['id']}"
        except:
            return None
    return None

# --- Improved Real Download Engine (403 Error Bypass) ---
def download_media_to_buffer(url, media_type='video', quality='720', audio_fmt='mp3'):
    temp_id = random.randint(1000, 9999)
    temp_name = f"download_{temp_id}"
    
    # YouTube က Bot ဟုတ်မဟုတ် စစ်ဆေးတာကို ကျော်ဖြတ်ရန် Headers များ
    common_opts = {
        'quiet': True,
        'no_warnings': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'referer': 'https://www.youtube.com/',
        'noprogress': True,
        'http_headers': {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        }
    }

    if media_type == 'video':
        ydl_opts = {
            **common_opts,
            'format': f'bestvideo[height<={quality}][ext=mp4]+bestaudio[ext=m4a]/best[height<={quality}][ext=mp4]/best',
            'outtmpl': f"{temp_name}.%(ext)s",
            'merge_output_format': 'mp4',
        }
    else:
        ydl_opts = {
            **common_opts,
            'format': 'bestaudio/best',
            'outtmpl': temp_name,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': audio_fmt,
                'preferredquality': '192',
            }],
        }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    
    # ဒေါင်းလုဒ်လုပ်ပြီးသားဖိုင်ကို ရှာဖွေခြင်း
    downloaded_file = None
    for f in os.listdir('.'):
        if f.startswith(temp_name):
            downloaded_file = f
            break
            
    if downloaded_file:
        with open(downloaded_file, 'rb') as f:
            data = f.read()
        os.remove(downloaded_file)
        return data
    else:
        raise Exception("File not found. FFmpeg installation or permissions might be the issue.")

# --- App State Management ---
if 'app_mode' not in st.session_state: st.session_state.app_mode = 'landing'
if 'selected_url' not in st.session_state: st.session_state.selected_url = None
if 'v_ready' not in st.session_state: st.session_state.v_ready = False

# ---------------------------------------------------------
# 1. LANDING PAGE
# ---------------------------------------------------------
if st.session_state.app_mode == 'landing':
    st.markdown("""
        <div class='landing-container'>
            <div style='font-size: 70px;'>🎬</div>
            <h1>Movie Recap Downloader</h1>
            <p style='color: #64748B; font-size: 18px;'>High-speed, handpicked, and eye-friendly design.</p>
        </div>
    """, unsafe_allow_html=True)

    col_l1, col_l2, col_l3 = st.columns([1, 0.4, 1])
    with col_l2:
        if st.button("🚀 Get Started"):
            st.session_state.selected_url = fetch_filtered_video("Trending")
            st.session_state.app_mode = 'dashboard'
            st.rerun()

# ---------------------------------------------------------
# 2. DASHBOARD
# ---------------------------------------------------------
elif st.session_state.app_mode == 'dashboard':
    with st.sidebar:
        st.markdown("### ⚙️ System Update")
        if st.button("🔄 Update Engine"):
            st.toast(update_library())
        st.divider()
        st.caption("UI Version: 3.2 (Bypass Fixed)")

    st.title("🎬 Download Dashboard")

    if st.session_state.selected_url:
        try:
            v_col, i_col = st.columns([3, 2], gap="large")

            with v_col:
                st.video(st.session_state.selected_url)

            with i_col:
                # Video Info extraction with error handling
                try:
                    with yt_dlp.YoutubeDL({'quiet': True, 'user_agent': 'Mozilla/5.0'}) as ydl:
                        info = ydl.extract_info(st.session_state.selected_url, download=False)
                        video_title = info.get('title', 'Video')
                        st.markdown(f"### {video_title}")
                        mins, secs = divmod(info.get('duration', 0), 60)
                        st.info(f"⏱️ Duration: {mins}m {secs}s")
                except:
                    video_title = "Video Recap"
                    st.warning("Could not fetch full metadata, but download may still work.")

                st.markdown("---")
                genre = st.selectbox("Movie Category:", ["Trending", "Horror", "Action", "Sci-Fi", "Thriller"])
                c1, c2 = st.columns(2)
                if c1.button("🔍 Find Recap"):
                    st.session_state.selected_url = fetch_filtered_video(genre)
                    st.session_state.v_ready = False
                    st.rerun()
                if c2.button("⏭️ Next Video"):
                    st.session_state.selected_url = fetch_filtered_video(genre)
                    st.session_state.v_ready = False
                    st.rerun()

            st.markdown("---")
            st.subheader("📥 Download Settings")
            
            with st.container():
                d1, d2, d3 = st.columns(3)
                quality = d1.selectbox("Quality:", ["1080", "720", "480"], index=1)
                audio_fmt = d2.selectbox("Audio Format:", ["mp3", "wav", "m4a"])
                folder_prefix = d3.text_input("Folder Name (Prefix):", "MyMovies")

                if st.button("⚡ Start High-Speed Download"):
                    try:
                        with st.status("Processing Download...", expanded=True) as status:
                            st.write("Fetching video data...")
                            st.session_state.v_data = download_media_to_buffer(st.session_state.selected_url, 'video', quality)
                            
                            st.write("Fetching audio data...")
                            st.session_state.a_data = download_media_to_buffer(st.session_state.selected_url, 'audio', quality, audio_fmt)
                            
                            st.session_state.v_ready = True
                            status.update(label="✅ Download Prepared!", state="complete")
                        st.balloons()
                    except Exception as e:
                        st.error(f"Download Failed: {str(e)}")

            # --- Save Buttons (Only show when data is ready) ---
            if st.session_state.v_ready:
                st.divider()
                st.success("Download Ready! Please save the files to your device.")
                save_col1, save_col2 = st.columns(2)

                # Clean Filename
                clean_name = "".join([c for c in video_title if c.isalnum() or c==' ']).strip().replace(' ', '_')

                with save_col1:
                    st.download_button(
                        label="💾 Save Video (.mp4)",
                        data=st.session_state.v_data,
                        file_name=f"{folder_prefix}_{clean_name}.mp4",
                        mime="video/mp4",
                        use_container_width=True
                    )

                with save_col2:
                    st.download_button(
                        label=f"💾 Save Audio (.{audio_fmt})",
                        data=st.session_state.a_data,
                        file_name=f"{folder_prefix}_{clean_name}.{audio_fmt}",
                        mime=f"audio/{audio_fmt}",
                        use_container_width=True
                    )
        except Exception as e:
            st.error(f"Dashboard Error: {e}")
