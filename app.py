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
    ydl_opts = {
        'quiet': True,
        'match_filter': yt_dlp.utils.match_filter_func('duration > 300 & duration < 900'),
        'extract_flat': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        search_results = ydl.extract_info(f"ytsearch10:{query} movie recap", download=False)
        entries = search_results.get('entries', [])
        if entries:
            selected = random.choice(entries)
            return f"https://www.youtube.com/watch?v={selected['id']}"
    return None


# --- Real Download Engine ---
def download_media_to_buffer(url, media_type='video', quality='720', audio_fmt='mp3'):
    temp_name = f"temp_{random.randint(1000, 9999)}"

    if media_type == 'video':
        # အသံမပါတဲ့ Video သီးသန့်ဆွဲရန်
        ydl_opts = {
            'format': f'bestvideo[height<={quality}][ext=mp4]',
            'outtmpl': temp_name + '.mp4',
            'quiet': True, 'noprogress': True,
        }
        out_file = temp_name + '.mp4'
    else:
        # အသံဖိုင် သီးသန့်ဆွဲရန် (FFmpeg လိုအပ်ပါသည်)
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': temp_name,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': audio_fmt,
                'preferredquality': '192',
            }],
            'quiet': True, 'noprogress': True,
        }
        out_file = temp_name + '.' + audio_fmt

    # Download Process
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    # ဖိုင်ကို ဖတ်ပြီး ပြန်ဖျက်ခြင်း (Storage မပြည့်အောင်)
    try:
        with open(out_file, 'rb') as f:
            data = f.read()
        os.remove(out_file)
        return data
    except FileNotFoundError:
        # အကယ်၍ format အမည်ကွဲလွဲသွားပါက ရှာဖွေပြီး ဖတ်ရန်
        for f in os.listdir('.'):
            if f.startswith(temp_name):
                with open(f, 'rb') as fp:
                    data = fp.read()
                os.remove(f)
                return data
        raise Exception("Download failed or FFmpeg missing.")


# --- App State ---
if 'app_mode' not in st.session_state: st.session_state.app_mode = 'landing'
if 'selected_url' not in st.session_state: st.session_state.selected_url = None

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
        st.caption("Policy ပြောင်းလဲမှုကြောင့် error တက်လျှင် Engine ကို update လုပ်ပေးပါ။")
        if st.button("🔄 Update Engine"):
            st.toast(update_library())
        st.divider()
        st.caption("UI Version: 3.1 (Final Release)")

    st.title("🎬 Download Dashboard")

    if st.session_state.selected_url:
        try:
            v_col, i_col = st.columns([3, 2], gap="large")

            with v_col:
                st.video(st.session_state.selected_url)

            with i_col:
                with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                    info = ydl.extract_info(st.session_state.selected_url, download=False)
                    st.markdown(f"### {info.get('title')}")
                    mins, secs = divmod(info.get('duration'), 60)
                    st.info(f"⏱️ Duration: {mins}m {secs}s")
                    st.write(f"👤 Channel: {info.get('uploader')}")

                st.markdown("---")
                genre = st.selectbox("Movie Category:", ["Trending", "Horror", "Action", "Sci-Fi", "Thriller"])
                c1, c2 = st.columns(2)
                if c1.button("🔍 Find Recap"):
                    st.session_state.selected_url = fetch_filtered_video(genre)
                    # Video အသစ်ရှာရင် Download Button တွေ ပျောက်သွားအောင် Reset လုပ်ခြင်း
                    st.session_state.v_ready = False
                    st.session_state.a_ready = False
                    st.rerun()
                if c2.button("⏭️ Next Video"):
                    st.session_state.selected_url = fetch_filtered_video(genre)
                    st.session_state.v_ready = False
                    st.session_state.a_ready = False
                    st.rerun()

            st.markdown("---")

            # Download Settings
            st.subheader("📥 Download Settings")
            with st.container():
                d1, d2, d3 = st.columns(3)
                quality = d1.selectbox("Quality:", ["1080", "720", "480"], index=1)
                audio_fmt = d2.selectbox("Audio Format:", ["mp3", "wav", "m4a"])
                folder_name = d3.text_input("Folder Name:", "MyMovies")

                if st.button("⚡ Start High-Speed Download"):
                    try:
                        # Step 1: Video (Real Download)
                        v_p = st.progress(0, text="Downloading Video File...")
                        st.session_state.v_data = download_media_to_buffer(st.session_state.selected_url, 'video',
                                                                           quality)
                        v_p.progress(100)
                        st.session_state.v_ready = True

                        # Step 2: Audio (Real Download)
                        a_p = st.progress(0, text="Extracting Audio Stream...")
                        st.session_state.a_data = download_media_to_buffer(st.session_state.selected_url, 'audio',
                                                                           quality, audio_fmt)
                        a_p.progress(100)
                        st.session_state.a_ready = True

                        st.success("✅ Download Ready! You can save the files below.")
                        st.balloons()
                    except Exception as e:
                        st.error(f"Download Failed: {e}. (Make sure FFmpeg is installed)")

            # 'Download Ready!' အဆင့်အောင်မြင်မှသာ Save Buttons များပေါ်လာမည်
            if st.session_state.get('v_ready') and st.session_state.get('a_ready'):
                st.divider()
                save_col1, save_col2 = st.columns(2)

                # ဖိုင်အမည်များကို သန့်စင်ခြင်း (Invalid Characters ဖယ်ထုတ်ရန်)
                safe_title = "".join(
                    [c for c in info.get('title', 'video') if c.isalpha() or c.isdigit() or c == ' ']).rstrip()

                with save_col1:
                    st.download_button(
                        label="💾 Save Video (.mp4)",
                        data=st.session_state.v_data,
                        file_name=f"{folder_name}_{safe_title}.mp4",
                        mime="video/mp4",
                        use_container_width=True
                    )

                with save_col2:
                    st.download_button(
                        label=f"💾 Save Audio (.{audio_fmt})",
                        data=st.session_state.a_data,
                        file_name=f"{folder_name}_{safe_title}.{audio_fmt}",
                        mime=f"audio/{audio_fmt}",
                        use_container_width=True
                    )
        except Exception as e:
            st.error(f"Something went wrong: {e}")
