import streamlit as st
import google.generativeai as genai

# Konfigurasi Halaman Streamlit
st.set_page_config(page_title="Chatbot AI Gemini", page_icon="🤖", layout="centered")
st.title("🤖 Chatbot AI Google Gemini")

# 1. Mengambil API Key dari Streamlit Secrets atau Sidebar
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
else:
    api_key = st.sidebar.text_input("Masukkan Google Gemini API Key:", type="password")

if not api_key:
    st.warning("⚠️ Silakan masukkan **GEMINI_API_KEY** di menu Secrets Streamlit Cloud atau di sidebar untuk memulai.")
    st.stop()

# Konfigurasi SDK Google Gemini
genai.configure(api_key=api_key)

# 2. Fungsi Otomatis Mencari Model Terbaca & Aktif (ANTI 404)
@st.cache_resource
def get_active_gemini_model():
    """
    Mendeteksi secara otomatis model Gemini yang tersedia dan bisa digunakan
    pada API Key yang terpasang agar tidak crash terkena Error 404.
    """
    try:
        # Mengambil semua model yang mendukung 'generateContent'
        available_models = [
            m.name for m in genai.list_models() 
            if 'generateContent' in m.supported_generation_methods
        ]
        
        # Urutan prioritas model dari yang terbaru
        preferred_models = [
            "models/gemini-2.5-flash",
            "models/gemini-2.0-flash",
            "models/gemini-1.5-flash",
            "models/gemini-1.5-pro",
            "models/gemini-pro"
        ]
        
        # Cek apakah ada model prioritas yang tersedia
        for model_path in preferred_models:
            if model_path in available_models:
                return model_path
                
        # Jika nama model di daftar tidak pakai prefix 'models/'
        for model_path in preferred_models:
            clean_name = model_path.replace("models/", "")
            for available in available_models:
                if clean_name in available:
                    return available

        # Jika tidak ada match khusus, gunakan model pertama yang tersedia
        if available_models:
            return available_models[0]

    except Exception as e:
        st.sidebar.error(f"Gagal memuat daftar model: {e}")
    
    # Fallback default jika list_models gagal
    return "gemini-2.5-flash"

# Deteksi Model
active_model_name = get_active_gemini_model()
st.sidebar.success(f"✅ Model terhubung: `{active_model_name}`")

# Inisialisasi GenerativeModel
try:
    model = genai.GenerativeModel(active_model_name)
except Exception as e:
    st.error(f"Gagal menghubungkan model `{active_model_name}`: {e}")
    st.stop()

# 3. Manajemen Riwayat Chat (Session State)
if "messages" not in st.session_state:
    st.session_state.messages = []

# Tampilkan riwayat percakapan sebelumnya
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 4. Input Pesan Pengguna
if prompt := st.chat_input("Ketik pesan Anda di sini..."):
    # Simpan dan tampilkan pesan pengguna
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Kirim ke Gemini API dan tampilkan respon
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        with st.spinner("Gemini sedang berpikir..."):
            try:
                response = model.generate_content(prompt)
                response_text = response.text
                response_placeholder.markdown(response_text)
                
                # Simpan respon asisten ke riwayat
                st.session_state.messages.append({"role": "assistant", "content": response_text})
            except Exception as e:
                response_placeholder.error(f"Terjadi kesalahan saat memproses respon: {e}")
