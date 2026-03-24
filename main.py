import streamlit as st
import streamlit.components.v1 as components
import base64
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
import datetime
import urllib.request
import urllib.parse
import json

# --- 1. Page Configuration ---
try:
    recaptcha_component = components.declare_component(
        "recaptcha_component",
        path="recaptcha_component"
    )
except Exception:
    recaptcha_component = None

st.set_page_config(
    page_title="早大学院生専用オンライン家庭教師 | 現役政経生による内部進学対策",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. Design System & Custom CSS ---
def local_css():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Noto+Serif+JP:wght@400;700;900&family=Noto+Sans+JP:wght@400;500;700&display=swap');

        :root {
            --waseda-red: #8E2034;
            --waseda-red-light: #B02E48;
            --waseda-red-dark: #6A1828;
            --bg-gray: #F9FAFB;
            --bg-white: #FFFFFF;
            --text-dark: #1F2937;
            --text-gray: #4B5563;
            --text-light: #9CA3AF;
            --border: #E5E7EB;
            --gold: #B8960C;
        }

        html, body, [class*="css"] {
            font-family: 'Noto Sans JP', sans-serif;
            color: var(--text-dark);
            background-color: var(--bg-gray);
        }
        h1, h2, h3 {
            font-family: 'Noto Serif JP', serif;
            color: var(--text-dark);
            font-weight: 700;
        }
        strong { color: var(--waseda-red); font-weight: 700; }

        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}

        /* ── Hero ── */
        .hero-container {
            background: linear-gradient(150deg, var(--waseda-red-dark) 0%, var(--waseda-red) 50%, #A52840 100%);
            color: white;
            padding: 7rem 2rem 5rem;
            text-align: center;
            border-radius: 0 0 60px 60px;
            margin-bottom: 5rem;
            box-shadow: 0 20px 40px -10px rgba(142, 32, 52, 0.4);
            position: relative;
            overflow: hidden;
        }
        .hero-container::before {
            content: "";
            position: absolute;
            inset: 0;
            background: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.03'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
        }
        .hero-eyebrow {
            display: inline-block;
            background: rgba(255,255,255,0.15);
            border: 2px solid rgba(255,255,255,0.5);
            border-radius: 60px;
            padding: 0.7rem 2.5rem;
            font-size: clamp(0.95rem, 3.5vw, 1.55rem);
            font-weight: 900;
            letter-spacing: 0.06em;
            margin-bottom: 2rem;
            color: #FFFFFF;
            font-family: 'Noto Serif JP', serif;
            text-shadow: 0 1px 6px rgba(0,0,0,0.25);
        }
        .hero-title {
            font-size: clamp(1.55rem, 5.5vw, 4.2rem);
            font-weight: 900;
            margin-bottom: 1.5rem;
            line-height: 1.3;
            color: white !important;
        }
        .hero-title .highlight {
            color: #FFD580 !important;
            font-style: normal;
        }
        .hero-subtitle {
            font-size: 1.15rem;
            margin-bottom: 2.5rem;
            opacity: 0.92;
            line-height: 1.9;
            max-width: 700px;
            margin-left: auto !important;
            margin-right: auto !important;
            text-align: center !important;
            display: block;
        }
        .hero-badges {
            display: flex;
            justify-content: center;
            gap: 1rem;
            flex-wrap: wrap;
            margin-bottom: 2.5rem;
        }
        .hero-badge {
            background: rgba(255,255,255,0.12);
            border: 1px solid rgba(255,255,255,0.25);
            border-radius: 8px;
            padding: 0.5rem 1rem;
            font-size: 0.88rem;
            color: white;
        }

        /* ── Buttons ── */
        div.stButton > button {
            background-color: var(--waseda-red);
            color: white !important;
            border: none;
            padding: 0.85rem 2.5rem;
            font-size: 1.05rem;
            font-weight: 700;
            border-radius: 50px;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(142,32,52,0.3);
        }
        div.stButton > button:hover {
            background-color: var(--waseda-red-light);
            transform: translateY(-2px);
            box-shadow: 0 10px 25px rgba(142,32,52,0.35);
            color: white !important;
        }
        div.stButton > button:active { transform: translateY(0); }

        /* ── Anchor CTA Button (scroll bug fix) ── */
        .btn-scroll {
            display: inline-block;
            background-color: var(--waseda-red);
            color: white !important;
            text-decoration: none;
            padding: 0.85rem 2.5rem;
            font-size: 1.1rem;
            font-weight: 700;
            border-radius: 50px;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(142,32,52,0.35);
            cursor: pointer;
            font-family: 'Noto Sans JP', sans-serif;
        }
        .btn-scroll:hover {
            background-color: var(--waseda-red-light);
            transform: translateY(-2px);
            box-shadow: 0 10px 25px rgba(142,32,52,0.4);
            color: white !important;
            text-decoration: none;
        }

        /* ── Section ── */
        .section-header {
            text-align: center;
            margin-bottom: 3rem;
        }
        .section-header h2 {
            font-size: clamp(1.6rem, 3vw, 2.4rem);
            margin-bottom: 0.75rem;
            display: inline-block;
            border-bottom: 4px solid var(--waseda-red);
            padding-bottom: 0.5rem;
        }
        .section-header p {
            color: var(--text-gray);
            font-size: 1rem;
            margin-top: 0.5rem;
        }
        .section-eyebrow {
            font-size: 0.8rem;
            letter-spacing: 0.12em;
            color: var(--waseda-red);
            font-weight: 700;
            text-transform: uppercase;
            margin-bottom: 0.5rem;
        }

        /* ── Cards ── */
        .card {
            background: white;
            padding: 2rem;
            border-radius: 20px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.06);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            height: 100%;
            border: 1px solid var(--border);
        }
        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 16px 32px rgba(0,0,0,0.1);
        }
        .card-icon { font-size: 2.8rem; margin-bottom: 1rem; text-align: center; }
        .card-title { font-size: 1.1rem; font-weight: 700; margin-bottom: 0.5rem; }

        /* ── Pain Points Grid ── */
        .pain-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 1.5rem;
            margin-bottom: 2rem;
        }
        @media (max-width: 768px) { .pain-grid { grid-template-columns: 1fr; } }

        /* ── Courses ── */
        .course-card {
            background: white;
            border-radius: 24px;
            overflow: hidden;
            box-shadow: 0 4px 16px rgba(0,0,0,0.08);
            border: 1px solid var(--border);
            height: 100%;
        }
        .course-header {
            padding: 1.75rem 2rem;
            background: linear-gradient(135deg, var(--waseda-red-dark), var(--waseda-red));
            color: white;
        }
        .course-header h3 { color: white !important; margin: 0; font-size: 1.2rem; }
        .course-header .course-tag {
            display: inline-block;
            background: rgba(255,255,255,0.2);
            border-radius: 50px;
            padding: 0.2rem 0.8rem;
            font-size: 0.75rem;
            margin-bottom: 0.75rem;
        }
        .course-body { padding: 1.75rem 2rem; }
        .course-item {
            display: flex;
            align-items: flex-start;
            gap: 0.75rem;
            margin-bottom: 1rem;
            font-size: 0.95rem;
        }
        .course-item-icon {
            flex-shrink: 0;
            width: 28px;
            height: 28px;
            background: #FEF2F2;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 0.8rem;
        }

        /* ── Instructor Profile ── */
        .profile-card {
            background: white;
            border-radius: 20px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.06);
            border: 1px solid var(--border);
            overflow: hidden;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        .profile-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 16px 32px rgba(0,0,0,0.1);
        }
        .profile-card-header {
            background: linear-gradient(135deg, var(--waseda-red-dark), var(--waseda-red));
            padding: 1.5rem 1rem 1rem;
            text-align: center;
        }
        .profile-avatar {
            width: 72px; height: 72px;
            background: rgba(255,255,255,0.2);
            border-radius: 50%;
            margin: 0 auto 0.75rem;
            display: flex; align-items: center; justify-content: center;
            font-size: 1.8rem;
            border: 3px solid rgba(255,255,255,0.5);
        }
        .profile-name { color: white !important; font-size: 1rem; font-weight: 700; margin: 0 0 0.25rem; }
        .profile-dept { color: rgba(255,255,255,0.8); font-size: 0.8rem; }
        .profile-card-body { padding: 1.25rem; }
        .profile-badge {
            display: inline-block;
            background: #FEF2F2;
            color: var(--waseda-red);
            border-radius: 50px;
            padding: 0.2rem 0.7rem;
            font-size: 0.75rem;
            font-weight: 700;
            margin: 0.2rem 0.15rem;
        }
        .profile-message {
            font-size: 0.85rem;
            color: var(--text-gray);
            line-height: 1.7;
            margin-top: 0.75rem;
            border-top: 1px solid var(--border);
            padding-top: 0.75rem;
        }

        /* ── Comparison Table ── */
        .compare-table {
            width: 100%;
            border-collapse: collapse;
            border-radius: 16px;
            overflow: hidden;
            box-shadow: 0 4px 16px rgba(0,0,0,0.08);
            font-size: 0.9rem;
        }
        .compare-table th {
            background: var(--waseda-red);
            color: white;
            padding: 1rem 1.25rem;
            text-align: center;
        }
        .compare-table th:first-child { text-align: left; background: var(--waseda-red-dark); }
        .compare-table td {
            padding: 0.9rem 1.25rem;
            border-bottom: 1px solid var(--border);
            background: white;
            text-align: center;
        }
        .compare-table td:first-child { text-align: left; font-weight: 600; background: #FAFAFA; }
        .compare-table tr:last-child td { border-bottom: none; }
        .compare-table tr:hover td { background: #FEF8F8; }

        /* ── Pricing ── */
        .pricing-card {
            background: white;
            border-radius: 20px;
            padding: 2rem;
            box-shadow: 0 4px 16px rgba(0,0,0,0.08);
            border: 1px solid var(--border);
            position: relative;
            overflow: hidden;
            transition: transform 0.3s ease;
        }
        .pricing-card:hover { transform: translateY(-4px); }
        .pricing-card.featured { border-color: var(--waseda-red); border-width: 2px; }
        .pricing-badge {
            position: absolute; top: 0; right: 0;
            background: var(--waseda-red);
            color: white;
            padding: 0.35rem 1rem;
            font-size: 0.75rem;
            font-weight: 700;
            border-bottom-left-radius: 12px;
        }
        .pricing-price {
            font-size: 2.5rem;
            font-weight: 900;
            color: var(--waseda-red);
            font-family: 'Noto Serif JP', serif;
        }
        .pricing-unit { font-size: 1rem; color: var(--text-gray); font-weight: 400; }
        .pricing-list { list-style: none; padding: 0; margin: 1.25rem 0 0; }
        .pricing-list li { padding: 0.45rem 0; border-bottom: 1px solid var(--border); font-size: 0.9rem; }
        .pricing-list li:last-child { border-bottom: none; }

        /* ── Contact Form ── */
        .stTextInput > div > div > input,
        .stTextArea > div > div > textarea,
        .stSelectbox > div > div > div {
            border-radius: 10px;
            border: 1px solid var(--border);
        }
        .stTextInput > div > div > input:focus,
        .stTextArea > div > div > textarea:focus {
            border-color: var(--waseda-red);
            box-shadow: 0 0 0 1px var(--waseda-red);
        }

        /* ── Divider ── */
        hr { border-color: var(--border); margin: 3rem 0; }

        /* ── Stats bar ── */
        .stats-bar {
            display: flex;
            justify-content: center;
            gap: 3rem;
            flex-wrap: wrap;
            padding: 2rem;
            background: white;
            border-radius: 20px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.06);
            border: 1px solid var(--border);
            margin: 0 0 4rem;
        }
        .stat-item { text-align: center; }
        .stat-number {
            font-size: 2rem;
            font-weight: 900;
            color: var(--waseda-red);
            font-family: 'Noto Serif JP', serif;
            line-height: 1;
        }
        .stat-label { font-size: 0.8rem; color: var(--text-gray); margin-top: 0.25rem; }

        /* ── Flow Steps ── */
        .flow-steps {
            display: flex;
            gap: 0;
            align-items: flex-start;
            margin: 0 0 2rem;
        }
        .flow-step {
            flex: 1;
            text-align: center;
            padding: 0 0.75rem;
            position: relative;
        }
        .flow-step:not(:last-child)::after {
            content: "→";
            position: absolute;
            right: -0.6rem;
            top: 1.1rem;
            font-size: 1.4rem;
            color: var(--waseda-red);
            font-weight: 900;
        }
        .flow-number {
            width: 52px; height: 52px;
            background: var(--waseda-red);
            color: white;
            border-radius: 50%;
            display: flex; align-items: center; justify-content: center;
            font-size: 1.3rem; font-weight: 900;
            margin: 0 auto 0.75rem;
            font-family: 'Noto Serif JP', serif;
            box-shadow: 0 4px 12px rgba(142,32,52,0.3);
        }
        .flow-title {
            font-weight: 700; font-size: 0.95rem;
            margin-bottom: 0.4rem; color: var(--text-dark);
        }
        .flow-desc {
            font-size: 0.82rem; color: var(--text-gray); line-height: 1.65;
        }
        .flow-card {
            background: white; border-radius: 16px;
            padding: 1.25rem 1rem;
            border: 1px solid var(--border);
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        }

        /* ── FAQ ── */
        .faq-header-label {
            font-size: 0.82rem; font-weight: 700;
            color: var(--waseda-red); letter-spacing: 0.1em;
            text-transform: uppercase; margin-bottom: 0.4rem;
        }

        /* ── Urgency Banner ── */
        .urgency-banner {
            background: #FEF2F2;
            border: 1.5px solid var(--waseda-red);
            border-radius: 12px;
            padding: 0.85rem 1.25rem;
            text-align: center;
            font-size: 0.92rem;
            font-weight: 700;
            color: var(--waseda-red);
            margin: 0 auto 2rem;
            max-width: 680px;
        }

        /* ════════════════════════════════════════
           RESPONSIVE / FLUID LAYOUT
           ════════════════════════════════════════ */


        /* 強みセクション h3 のfluid typography */
        .feature-h3 {
            font-size: clamp(1.2rem, 2.8vw, 2rem);
            margin-bottom: 0.75rem;
            font-family: 'Noto Serif JP', serif;
            font-weight: 700;
        }

        /* 比較表：PC では横スクロールをラップ */
        .compare-table-wrap {
            overflow-x: auto;
            -webkit-overflow-scrolling: touch;
        }

        /* ── Mobile (≤ 768px) ── */
        @media (max-width: 768px) {

            /* Streamlit コンテナのマージン */
            .block-container {
                padding-left: 5% !important;
                padding-right: 5% !important;
                padding-top: 0 !important;
            }

            /* Hero */
            .hero-container {
                padding: 3rem 1rem 2.5rem !important;
                border-radius: 0 0 28px 28px !important;
                margin-bottom: 2rem !important;
            }
            .hero-eyebrow {
                padding: 0.5rem 1.1rem !important;
                letter-spacing: 0.03em !important;
                margin-bottom: 1.25rem !important;
            }
            .hero-subtitle {
                font-size: 0.95rem !important;
                line-height: 1.75 !important;
                max-width: 100% !important;
            }
            .hero-badges { gap: 0.4rem !important; }
            .hero-badge {
                font-size: 0.75rem !important;
                padding: 0.35rem 0.6rem !important;
            }

            /* CTAボタン */
            .btn-scroll {
                font-size: 0.95rem !important;
                padding: 0.7rem 1.6rem !important;
            }

            /* Stats bar */
            .stats-bar {
                gap: 1.25rem !important;
                padding: 1rem 0.75rem !important;
                margin-bottom: 2rem !important;
            }
            .stat-number { font-size: 1.4rem !important; }
            .stat-label  { font-size: 0.72rem !important; }

            /* セクションヘッダー */
            .section-header { margin-bottom: 1.5rem !important; }
            .section-header p { font-size: 0.88rem !important; }

            /* 強みh3 */
            .feature-h3 { font-size: 1.25rem !important; }

            /* カード */
            .card { padding: 1.1rem !important; }
            .card-title { font-size: 1rem !important; }

            /* 講師プロフィール */
            .profile-card-body { padding: 0.85rem !important; }
            .profile-message { font-size: 0.8rem !important; }

            /* 料金カード */
            .pricing-card { padding: 1.25rem !important; }
            .pricing-price { font-size: 1.8rem !important; }

            /* 比較表：横スクロール対応 */
            .compare-table { font-size: 0.76rem !important; }
            .compare-table th,
            .compare-table td { padding: 0.55rem 0.6rem !important; }

            /* Streamlit columns → モバイルで縦積み */
            [data-testid="stHorizontalBlock"] {
                flex-direction: column !important;
                gap: 1rem !important;
            }
            [data-testid="column"] {
                width: 100% !important;
                flex: 1 1 100% !important;
                min-width: 100% !important;
            }

            /* フォーム入力：iOS zoom 防止（16px以下でズームが発生する） */
            .stTextInput  > div > div > input,
            .stTextArea   > div > div > textarea,
            .stSelectbox  > div > div > div {
                font-size: 16px !important;
            }

            /* フォームボタン */
            .stFormSubmitButton > button {
                font-size: 0.95rem !important;
                padding: 0.7rem 1rem !important;
            }

            /* divider の余白を縮小 */
            hr { margin: 1.5rem 0 !important; }

            /* Flow: モバイルで縦積み */
            .flow-steps {
                flex-direction: column !important;
                gap: 1.5rem !important;
            }
            .flow-step {
                padding: 0 !important;
            }
            .flow-step:not(:last-child)::after {
                content: "↓" !important;
                position: static !important;
                display: block;
                margin: 0.5rem auto 0;
                font-size: 1.2rem !important;
            }

            /* 緊急バナー */
            .urgency-banner {
                font-size: 0.82rem !important;
                padding: 0.7rem 0.9rem !important;
            }
        }

    </style>
    """, unsafe_allow_html=True)

local_css()

# --- SEO / SNS Meta Tags ---
st.markdown("""
    <meta name="description"
          content="早大学院OBの現役政経生による、評定管理と大学準備に特化した家庭教師サービス。週2回の徹底サポート。">
    <meta property="og:title"
          content="早大学院生専用オンライン家庭教師 | 現役政経生による内部進学対策">
    <meta property="og:description"
          content="早大学院OBの現役政経生による、評定管理と大学準備に特化した家庭教師サービス。週2回の徹底サポート。">
    <meta property="og:type" content="website">
    <meta name="twitter:card" content="summary">
    <meta name="twitter:title"
          content="早大学院生専用オンライン家庭教師 | 現役政経生による内部進学対策">
    <meta name="twitter:description"
          content="早大学院OBの現役政経生による、評定管理と大学準備に特化した家庭教師サービス。週2回の徹底サポート。">
""", unsafe_allow_html=True)

# --- Scroll Preservation ---
def inject_scroll_preservation():
    components.html("""
        <script>
            var attempts = 0;
            var maxAttempts = 20;
            var targetScroll = sessionStorage.getItem('scrollPosition');
            if (targetScroll) {
                targetScroll = parseInt(targetScroll);
                var restoreInterval = setInterval(function() {
                    if (window.parent) {
                        window.parent.scrollTo(0, targetScroll);
                        if (Math.abs(window.parent.scrollY - targetScroll) < 10 || attempts >= maxAttempts) {
                            clearInterval(restoreInterval);
                        }
                        attempts++;
                    } else { clearInterval(restoreInterval); }
                }, 100);
            }
            if (window.parent) {
                window.parent.addEventListener('scroll', function() {
                    sessionStorage.setItem('scrollPosition', window.parent.scrollY);
                });
            }
        </script>
    """, height=0)

# --- 3. Utility ---
def get_image_as_base64(file_path):
    with open(file_path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

def send_email(name, user_email, grade, desired_dept, strengthen_subjects, subject, message):
    try:
        sender_email = st.secrets["email"]["address"]
        sender_password = st.secrets["email"]["password"]
        receiver_email = sender_email
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = receiver_email
        msg['Subject'] = f"【Gakuin Tutor】新規お問い合わせ: {name}様"
        subjects_str = ", ".join(strengthen_subjects) if strengthen_subjects else "なし"
        body = f"""
新規のお問い合わせがありました。

■お名前: {name}
■メールアドレス: {user_email}
■学年: {grade}
■志望学部: {desired_dept}
■強化したい科目: {subjects_str}
■相談科目(概要): {subject}

■詳細:
{message}
        """
        msg.attach(MIMEText(body, 'plain'))
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print(f"メール送信エラー: {e}")
        return False

def save_to_sheet(name, user_email, grade, desired_dept, strengthen_subjects, subject, message, date):
    url = "https://script.google.com/macros/s/AKfycbwJBvluzWVcpFZ2CeFS-dSL80iPXabCBeT1JlUdwaQn6GqSc6Wok3UouVj7lyyr8m7hng/exec"
    payload = {
        "name": name,
        "grade": grade,
        "faculty": desired_dept,
        "subjects": ", ".join(strengthen_subjects) if strengthen_subjects else "なし",
        "message": f"【件名】{subject}\n\n{message}",
        "email": user_email,
        "date": str(date)
    }
    try:
        response = requests.post(url, json=payload)
        try:
            result = response.json()
            if "debug_log" in result:
                st.info(f"GAS Debug Log: {result['debug_log']}")
            if result.get("status") == "error":
                st.error(f"GAS Logic Error: {result.get('message')}")
                return False
        except:
            pass
        if response.status_code != 200:
            st.error(f"GAS Error ({response.status_code}): {response.text}")
        return response.status_code == 200
    except Exception as e:
        st.error(f"Connection Error: {e}")
        return False


# ─────────────────────────────────────────
# SECTION COMPONENTS
# ─────────────────────────────────────────

def hero_section():
    st.markdown("""
        <div class="hero-container">
            <div class="hero-eyebrow">🎓 早大学院生 専用 オンライン家庭教師</div>
            <h1 class="hero-title">
                政経進学を確実にする、<br>
                <em class="highlight">評定管理</em>と<em class="highlight">大学先取り教育</em>。
            </h1>
            <p class="hero-subtitle" style="text-align:center;margin-left:auto;margin-right:auto;">
                講師は全員、学院から政治経済学部へ進んだ現役早大生。<br>
                評定 85 点以上・特別考査上位の実績を持つ先輩が、<br>
                あなたのお子さんの内部進学を徹底的にサポートします。
            </p>
            <div class="hero-badges">
                <span class="hero-badge">📊 評定85点以上の講師のみ在籍</span>
                <span class="hero-badge">🔬 特考対策・第二外国語に完全対応</span>
                <span class="hero-badge">🏛️ 大学入学後の先取り学習まで</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # CTA: HTMLアンカー — st.markdown はメインDOMに直接レンダリングされるため
    # window.parent 不要。document.getElementById で確実にスクロール。
    st.markdown("""
        <div style="text-align:center;margin-bottom:3rem;">
            <a class="btn-scroll"
               href="#contact"
               onclick="var el=document.getElementById('contact'); if(el){el.scrollIntoView({behavior:'smooth'});}; return false;">
                相談に申し込む(無料)
            </a>
        </div>
    """, unsafe_allow_html=True)

    # Stats bar
    st.markdown("""
        <div class="stats-bar">
            <div class="stat-item">
                <div class="stat-number">85+</div>
                <div class="stat-label">全講師の内部進学評定</div>
            </div>
            <div class="stat-item">
                <div class="stat-number">4</div>
                <div class="stat-label">対応第二外国語</div>
            </div>
            <div class="stat-item">
                <div class="stat-number">政経</div>
                <div class="stat-label">最難関学部への実績</div>
            </div>
            <div class="stat-item">
                <div class="stat-number">月額制</div>
                <div class="stat-label">週2回・入会金なし</div>
            </div>
        </div>
    """, unsafe_allow_html=True)


def pain_points_section():
    st.markdown("""
        <div class="section-header">
            <div class="section-eyebrow">PARENT'S CONCERN</div>
            <h2>こんな不安、ありませんか？</h2>
            <p>学院の保護者だからこそ感じる、内部進学特有の悩みに答えます。</p>
        </div>
    """, unsafe_allow_html=True)

    try:
        icon_b64 = get_image_as_base64("assets/pronunciation_icon.png")
        icon_html = f'<img src="data:image/png;base64,{icon_b64}" style="width:64px;height:64px;object-fit:contain;margin-bottom:0.75rem;">'
    except Exception:
        icon_html = '<div style="font-size:2.5rem;text-align:center;margin-bottom:0.75rem;">🌐</div>'

    st.markdown(f"""
        <div class="pain-grid">
            <div class="card">
                <div style="text-align:center;">{icon_html}</div>
                <div class="card-title">第二外国語が足を引っ張っている</div>
                <p style="font-size:0.9rem;color:#555;line-height:1.7;">
                    ドイツ語・中国語・フランス語・ロシア語——進級・内部進学の評定を左右する重要科目なのに、
                    対策できる塾がどこにもない。一般の家庭教師は制度すら知らない。
                </p>
            </div>
            <div class="card">
                <div class="card-icon" style="text-align:center;">⚖️</div>
                <div class="card-title">政経ボーダーに届くか不安</div>
                <p style="font-size:0.9rem;color:#555;line-height:1.7;">
                    政治経済学部への内部進学は評定上位者のみ。
                    「今の平均点で政経に届くのか」「特考でどれだけ挽回できるか」——
                    数字で答えられる先輩がいない。
                </p>
            </div>
            <div class="card">
                <div class="card-icon" style="text-align:center;">🚀</div>
                <div class="card-title">進学確定後、何をすれば？</div>
                <p style="font-size:0.9rem;color:#555;line-height:1.7;">
                    内部進学が決まったあとの「準備の空白」は、大学入学後に必ず差となって現れる。
                    受験生が勉強している間、学院生は何をすべきか知っている先輩が必要。
                </p>
            </div>
        </div>
    """, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)


def features_section():
    st.markdown("""
        <div class="section-header">
            <div class="section-eyebrow">WHY GAKUIN TUTOR</div>
            <h2>学院OBにしかできない指導</h2>
            <p>「学院を知っている」と「学院から政経に行った」は、まったく別次元の話です。</p>
        </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown("""
        <div style="padding:0.5rem;">
            <h3 class="feature-h3">🎓 講師全員が「学院→政経」ルート</h3>
            <p style="font-size:1rem;line-height:1.9;color:#374151;">
                教えるのは<strong>評定85点以上・特考上位</strong>で政経へ内部進学した現役早大生のみ。
                同じカリキュラム、同じ先生の採点傾向、同じプレッシャーを乗り越えた経験が、
                一般講師との圧倒的な差を生みます。<br><br>
                「内部進学で政経を目指す」という文脈で、教科指導から学部選択の相談まで一貫して対応できるのは、
                この道を歩んだ先輩だけです。
            </p>
        </div>
        """, unsafe_allow_html=True)
        try:
            img_b64 = get_image_as_base64("assets/waseda_classroom_new.jpg")
            st.markdown(f'<img src="data:image/jpeg;base64,{img_b64}" style="width:100%;aspect-ratio:4/3;object-fit:cover;border-radius:16px;box-shadow:0 4px 12px rgba(0,0,0,0.1);margin-top:1rem;">', unsafe_allow_html=True)
        except Exception:
            st.image("https://images.unsplash.com/photo-1523240795612-9a054b0db644?auto=format&fit=crop&q=80&w=800", use_container_width=True)

    with col2:
        st.markdown("""
        <div style="padding:0.5rem;">
            <h3 class="feature-h3">📊 評定を「取るための勉強」に変える</h3>
            <p style="font-size:1rem;line-height:1.9;color:#374151;">
                学院の評定は、なんとなくの勉強では上がりません。
                <strong>教員ごとの出題傾向・採点基準・特考との配点バランス</strong>を把握したうえで、
                戦略的に点数を積み上げる必要があります。<br><br>
                高1の段階から評定の推移を設計し、高3の志望学部申告時に確実に
                希望学部のボーダーを越えられる状態を作ります。
                「あの時もっと早く始めておけば」をなくすために。
            </p>
        </div>
        """, unsafe_allow_html=True)
        try:
            img_b64 = get_image_as_base64("assets/waseda_okuma_statue.jpg")
            st.markdown(f'<img src="data:image/jpeg;base64,{img_b64}" style="width:100%;aspect-ratio:4/3;object-fit:cover;border-radius:16px;box-shadow:0 4px 12px rgba(0,0,0,0.1);margin-top:1rem;">', unsafe_allow_html=True)
        except Exception:
            st.image("https://images.unsplash.com/photo-1434030216411-0b793f4b4173?auto=format&fit=crop&q=80&w=800", use_container_width=True)

    st.markdown("<br><br>", unsafe_allow_html=True)




def instructors_section():
    st.markdown("""
        <div class="section-header">
            <div class="section-eyebrow">OUR INSTRUCTORS</div>
            <h2>講師陣のご紹介</h2>
            <p>全員が学院から早稲田へ内部進学。評定 85 点以上・特考上位の実績者のみ。</p>
        </div>
    """, unsafe_allow_html=True)

    instructors = [
        {
            "name": "K.S 先輩",
            "dept": "政治経済学部 経済学科 2年",
            "badges": ["評定 87点", "特考 上位5%", "ドイツ語 得意"],
            "strength": "数学・ドイツ語・経済学",
            "message": "高2の夏まで政経は無理だと思っていました。二外を武器に変えてからが本番。「評定は科目の組み合わせで作るもの」という考え方を一緒に身につけましょう。"
        },
        {
            "name": "T.M 先輩",
            "dept": "政治経済学部 政治学科 2年",
            "badges": ["評定 85点", "特考 平均9点台", "英語 得意"],
            "strength": "英語・数学・論文読解",
            "message": "入学後、最初のレポートで周りとの差を実感しました。「書き方の型」を知っているだけで大学の評価は別物になります。入学前に一緒に準備しましょう。"
        },
        {
            "name": "Y.O 先輩",
            "dept": "創造理工学部 3年",
            "badges": ["評定 86点", "理系科目 全般", "物理・化学 得意"],
            "strength": "物理・化学・数学",
            "message": "理系学部への内部進学は数学と理科の評定が勝負。特考の記述で「部分点をどれだけ取るか」の戦略を徹底的に教えます。"
        },
        {
            "name": "H.A 先輩",
            "dept": "商学部 2年",
            "badges": ["評定 85点", "中国語検定取得", "英語・中国語 得意"],
            "strength": "英語・中国語・マーケティング",
            "message": "中国語は正しい方法で勉強すれば必ず得点源になります。商学部を目指すなら英語と中国語のダブルアドバンテージで評定を底上げしましょう。"
        },
    ]

    cols = st.columns(4)
    for i, inst in enumerate(instructors):
        badges_html = "".join([f'<span class="profile-badge">{b}</span>' for b in inst["badges"]])
        with cols[i]:
            st.markdown(f"""
                <div class="profile-card">
                    <div class="profile-card-header">
                        <div class="profile-avatar">👨‍🎓</div>
                        <div class="profile-name">{inst['name']}</div>
                        <div class="profile-dept">{inst['dept']}</div>
                    </div>
                    <div class="profile-card-body">
                        <div style="margin-bottom:0.5rem;">{badges_html}</div>
                        <div style="font-size:0.8rem;color:#555;margin-top:0.5rem;">
                            <strong style="color:#1F2937;">得意科目：</strong>{inst['strength']}
                        </div>
                        <div class="profile-message">
                            💬 「{inst['message']}」
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)


def comparison_section():
    st.markdown("""
        <div class="section-header">
            <div class="section-eyebrow">COMPARISON</div>
            <h2>他サービスとの違い</h2>
            <p>「学院を知っている」と「学院から政経に進んだ」は別次元です。</p>
        </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        st.markdown("""
        <div class="compare-table-wrap">
        <table class="compare-table">
            <thead>
                <tr>
                    <th>比較項目</th>
                    <th>大手家庭教師センター</th>
                    <th>Gakuin Tutor</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>内部進学の経験</td>
                    <td>❌ ほぼなし</td>
                    <td>✅ 講師全員が経験者</td>
                </tr>
                <tr>
                    <td>評定システムの理解（特考・100点制）</td>
                    <td>❌ 制度を知らない</td>
                    <td>✅ 自分が受けた制度</td>
                </tr>
                <tr>
                    <td>政経ボーダーの「肌感覚」</td>
                    <td>❌ 数字しか知らない</td>
                    <td>✅ その数字を越えた実績</td>
                </tr>
                <tr>
                    <td>教員ごとの出題・採点傾向の把握</td>
                    <td>❌ 不可能</td>
                    <td>✅ OBネットワークで共有</td>
                </tr>
                <tr>
                    <td>第二外国語（独・仏・露・中）対応</td>
                    <td>❌ 対応不可が大半</td>
                    <td>✅ 学院で履修した言語を指導</td>
                </tr>
                <tr>
                    <td>大学入学後の「リアルな準備」指導</td>
                    <td>❌ 経験なし</td>
                    <td>✅ 政経・商・理工の在学生が対応</td>
                </tr>
            </tbody>
        </table>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)


def flow_section():
    st.markdown("""
        <div class="section-header">
            <div class="section-eyebrow">HOW IT WORKS</div>
            <h2>指導開始までの流れ</h2>
            <p>お申し込みから指導スタートまで、最短1週間で開始できます。</p>
        </div>
        <div class="flow-steps">
            <div class="flow-step">
                <div class="flow-card">
                    <div class="flow-number">1</div>
                    <div class="flow-title">無料相談お申し込み</div>
                    <div class="flow-desc">フォームより学年・志望学部・強化したい科目を送信。2営業日以内にご連絡します。</div>
                </div>
            </div>
            <div class="flow-step">
                <div class="flow-card">
                    <div class="flow-number">2</div>
                    <div class="flow-title">オンライン面談</div>
                    <div class="flow-desc">現役政経生スタッフによる状況ヒアリングと評定ロードマップのご提案。所要30分程度。</div>
                </div>
            </div>
            <div class="flow-step">
                <div class="flow-card">
                    <div class="flow-number">3</div>
                    <div class="flow-title">体験指導（60分）</div>
                    <div class="flow-desc">担当講師による実際の指導を体験。相性・スタイルをご確認いただけます。</div>
                </div>
            </div>
            <div class="flow-step">
                <div class="flow-card">
                    <div class="flow-number">4</div>
                    <div class="flow-title">本契約・指導開始</div>
                    <div class="flow-desc">ご契約後、週2回・月8回の定額指導をスタート。月次レポートで保護者様にもご報告。</div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)


def faq_section():
    st.markdown("""
        <div class="section-header">
            <div class="section-eyebrow">FAQ</div>
            <h2>よくある質問</h2>
            <p>お申し込み前によくいただくご質問をまとめました。</p>
        </div>
    """, unsafe_allow_html=True)

    faqs = [
        (
            "指導はどのような形式で行われますか？",
            "Google Meet または Zoom を使用した、完全オンラインの1対1指導です。専用の教材・ホワイトボードツールを活用し、対面授業と同水準の指導をご提供します。"
        ),
        (
            "講師の変更は可能ですか？",
            "はい、可能です。お子様との相性を最優先に考慮しております。体験指導後や指導開始後でも、ご要望があればいつでも講師変更のご相談を承ります。"
        ),
        (
            "支払方法を教えてください。",
            "クレジットカード決済または銀行振込に対応しております。詳細はオンライン面談の際にご案内いたします。月額制・前払い（当月分を前月末までにお支払い）となります。"
        ),
        (
            "第二外国語だけでも受講できますか？",
            "はい、可能です。ドイツ語・フランス語・ロシア語・中国語の各専門講師が在籍しております。スポット単発での受講もお気軽にご相談ください。"
        ),
        (
            "中学部の生徒も受講できますか？",
            "はい、早大学院中学部の在校生も対象としております。高校内部進学を見据えた基礎固めから、定期テスト対策まで幅広くサポートします。"
        ),
        (
            "途中で退会することはできますか？",
            "前月15日までにお申し出いただければ、翌月から退会が可能です。違約金等は一切発生しません。"
        ),
    ]

    _, col_faq, _ = st.columns([1, 5, 1])
    with col_faq:
        for q, a in faqs:
            with st.expander(f"Q：{q}"):
                st.markdown(f"""
                    <div style="padding:0.5rem 0.25rem;font-size:0.95rem;line-height:1.8;color:#374151;">
                        <span style="font-weight:700;color:var(--waseda-red,#8E2034);">A：</span>{a}
                    </div>
                """, unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)


def pricing_section():
    st.markdown("""
        <div class="section-header">
            <div class="section-eyebrow">PRICING</div>
            <h2>料金プラン</h2>
            <p>全プラン共通：<strong>週2回（月8回）固定</strong>の月額制。入会金・教材費は一切かかりません。</p>
        </div>
    """, unsafe_allow_html=True)

    col0, col1, col2, col3 = st.columns(4, gap="medium")

    with col0:
        st.markdown("""
        <div class="pricing-card" style="border-top: 4px solid #2563EB;">
            <h3 style="font-size:1.05rem;margin-bottom:0.25rem;">🏫 中学部 基礎固めプラン</h3>
            <p style="font-size:0.82rem;color:#666;margin-bottom:1rem;">中学部在校生・保護者向け</p>
            <div class="pricing-price" style="font-size:2rem;">¥40,000<span class="pricing-unit"> / 月（税込）</span></div>
            <p style="font-size:0.78rem;color:#888;margin:0.25rem 0 1rem;">週2回・月8回 固定</p>
            <ul class="pricing-list">
                <li>✅ 定期テスト対策（全教科）</li>
                <li>✅ 高校内部進学を見据えた記述力強化</li>
                <li>✅ 数学・英語の基礎徹底</li>
                <li>✅ LINEでの質問サポート</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    with col1:
        st.markdown("""
        <div class="pricing-card">
            <h3 style="font-size:1.05rem;margin-bottom:0.25rem;">A. スタンダード</h3>
            <p style="font-size:0.82rem;color:#666;margin-bottom:1rem;">内部進学の基礎固めに</p>
            <div class="pricing-price" style="font-size:2rem;">¥40,000<span class="pricing-unit"> / 月（税込）</span></div>
            <p style="font-size:0.78rem;color:#888;margin:0.25rem 0 1rem;">週2回・月8回 固定</p>
            <ul class="pricing-list">
                <li>✅ 定期テスト・特考対策</li>
                <li>✅ 第二外国語（独・仏・露・中）</li>
                <li>✅ 全教科対応</li>
                <li>✅ LINEでの質問サポート</li>
                <li>✅ 評定ロードマップ設計（初回）</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="pricing-card featured">
            <div class="pricing-badge">おすすめ</div>
            <h3 style="font-size:1.05rem;margin-bottom:0.25rem;">B. プレミアム</h3>
            <p style="font-size:0.82rem;color:#666;margin-bottom:1rem;">政経ボーダー突破に</p>
            <div class="pricing-price" style="font-size:2rem;">¥50,000<span class="pricing-unit"> / 月（税込）</span></div>
            <p style="font-size:0.78rem;color:#888;margin:0.25rem 0 1rem;">週2回・月8回 固定</p>
            <ul class="pricing-list">
                <li>✅ スタンダードの全内容</li>
                <li>✅ 月次評定レポート（保護者向け）</li>
                <li>✅ 学部別ボーダー管理シート</li>
                <li>✅ 学院OBネットワーク情報共有</li>
                <li>✅ 緊急フォロー授業（テスト前）</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="pricing-card">
            <h3 style="font-size:1.05rem;margin-bottom:0.25rem;">C. プラチナ</h3>
            <p style="font-size:0.82rem;color:#666;margin-bottom:1rem;">大学まで見据えた完全サポート</p>
            <div class="pricing-price" style="font-size:2rem;">¥60,000<span class="pricing-unit"> / 月（税込）</span></div>
            <p style="font-size:0.78rem;color:#888;margin:0.25rem 0 1rem;">週2回・月8回 固定</p>
            <ul class="pricing-list">
                <li>✅ プレミアムの全内容</li>
                <li>✅ 早大入学準備プログラム込み</li>
                <li>✅ アカデミックライティング指導</li>
                <li>✅ キャリア・ゼミ選び 先輩面談</li>
                <li>✅ TOEIC・学術英語対策</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)


def contact_section():
    st.markdown("""
        <div id="contact" class="section-header">
            <div class="section-eyebrow">FREE CONSULTATION</div>
            <h2>無料相談・お申し込み</h2>
            <p>現在の評定と志望学部をお教えください。<br>
            政経進学に向けた具体的な戦略を、現役政経生講師がご提案します。</p>
        </div>
    """, unsafe_allow_html=True)

    # 「まずは気軽に」— フォーム直上に配置
    st.markdown("""
        <div style="max-width:680px;margin:0 auto 2.5rem;background:white;border-radius:20px;
                    padding:1.75rem 2rem;border:1px solid #E5E7EB;
                    box-shadow:0 2px 8px rgba(0,0,0,0.06);text-align:center;">
            <div style="font-size:2rem;margin-bottom:0.5rem;">📞</div>
            <div style="font-weight:700;font-size:1.1rem;margin-bottom:0.5rem;
                        font-family:'Noto Serif JP',serif;">まずは気軽にご相談ください</div>
            <p style="font-size:0.9rem;color:#555;line-height:1.7;margin-bottom:1rem;">
                現在の評定・志望学部を教えていただくだけで、<br>
                政経ボーダーまでの差と対策方針をお伝えします。
            </p>
            <div style="display:flex;justify-content:center;gap:1.5rem;flex-wrap:wrap;font-size:0.88rem;color:#444;">
                <span>✅ 完全無料</span>
                <span>✅ 入会の強制なし</span>
                <span>✅ 2営業日以内にご返信</span>
                <span>✅ オンライン完結</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("""
        <div class="urgency-banner">
            ⚠️ 講師の質を維持するため、今月の新規受付は残り <u>3名様</u> までとさせていただいております。
        </div>
    """, unsafe_allow_html=True)

    _, col_form, _ = st.columns([1, 4, 1])

    with col_form:
        with st.form("contact_form"):
            r1c1, r1c2 = st.columns(2)
            with r1c1:
                name = st.text_input("お名前 （必須）", placeholder="早稲田太郎")
                email = st.text_input("メールアドレス （必須）", placeholder="example@email.com")
                grade = st.selectbox("お子さんの学年 （必須）", [
                    "中学1年生", "中学2年生", "中学3年生",
                    "高校1年生", "高校2年生", "高校3年生",
                    "大学1年生（準備中）"
                ])
            with r1c2:
                desired_dept = st.selectbox("第一志望学部 （必須）", [
                    "政治経済学部", "法学部", "商学部", "社会科学部", "教育学部",
                    "文学部", "文化構想学部", "基幹理工学部", "創造理工学部",
                    "先進理工学部", "人間科学部", "スポーツ科学部", "未定"
                ])
                strengthen_subjects = st.multiselect("強化したい科目 （複数可・必須）", [
                    "英語", "数学", "国語",
                    "理科（物理・化学・生物）",
                    "社会（地歴・公民）",
                    "第二外国語（ドイツ語）",
                    "第二外国語（フランス語）",
                    "第二外国語（ロシア語）",
                    "第二外国語（中国語）",
                    "大学入学準備（レポート・英語等）"
                ])
                subject = st.text_input("ご相談の件名 （必須）", placeholder="例：政経ボーダーに向けた評定対策について")

            date_col, time_col = st.columns(2)
            with date_col:
                date = st.date_input("面談希望日", min_value=datetime.date.today())
            with time_col:
                preferred_time = st.selectbox("面談希望時間", [
                    "17:00", "17:30", "18:00", "18:30", "19:00",
                    "19:30", "20:00", "20:30", "21:00", "21:30", "22:00"
                ])

            message = st.text_area("詳細なご相談内容（任意）", height=130,
                placeholder="現在の評定の状況、特に困っている科目、目指している学部など、何でもお書きください。")

            # reCAPTCHA
            site_key = st.secrets["recaptcha"]["site_key"]
            recaptcha_token = recaptcha_component(site_key=site_key, key="recaptcha")

            # Privacy Policy
            st.markdown("""
<div style="margin-top:16px;margin-bottom:20px;font-size:11px;color:#888;line-height:1.6;">
    <p style="text-align:center;margin-bottom:12px;">送信ボタンを押すことで、以下のプライバシーポリシーに同意したものとみなされます。</p>
    <details style="background:#f9f9f9;border-radius:8px;padding:12px;border:1px solid #e5e7eb;">
        <summary style="cursor:pointer;font-weight:bold;color:#555;">【プライバシーポリシー】（クリックで展開）</summary>
        <div style="margin-top:10px;">
        <p>早大学院生専用家庭教師 事務局（以下「当方」）は、本サービスにおけるユーザーの個人情報の取扱いについて以下のとおりプライバシーポリシーを定めます。</p>
        <p><strong>第1条（個人情報）</strong><br>
        「個人情報」とは、氏名・メールアドレス・学年・志望学部・学習状況等により特定の個人を識別できる情報を指します。</p>
        <p><strong>第2条（収集・利用目的）</strong><br>
        ①体験授業・指導の日程調整 ②お問い合わせへの回答 ③指導カリキュラム作成 ④不正利用者の特定</p>
        <p><strong>第3条（管理・セキュリティ）</strong><br>
        お預かりした個人情報は、Google Workspace 等のセキュリティ基準を有するクラウドサービスにより厳重に管理します。</p>
        <p><strong>第4条（第三者提供の禁止）</strong><br>
        法令上の義務がある場合等を除き、ユーザーの同意なく第三者に個人情報を提供しません。</p>
        <p><strong>第5条（開示・訂正・削除）</strong><br>
        本人確認の上、速やかに対応いたします。お問い合わせフォームよりご連絡ください。</p>
        </div>
    </details>
</div>
""", unsafe_allow_html=True)

            submit_btn = st.form_submit_button("評定診断・無料相談を申し込む →", use_container_width=True)

            import re
            email_pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
            is_valid_email = re.match(email_pattern, email) is not None if email else False

            def verify_recaptcha_token(token):
                if not token:
                    return False
                secret_key = st.secrets["recaptcha"]["secret_key"]
                url = "https://www.google.com/recaptcha/api/siteverify"
                data = urllib.parse.urlencode({'secret': secret_key, 'response': token}).encode()
                try:
                    req = urllib.request.Request(url, data=data)
                    with urllib.request.urlopen(req) as response:
                        result = json.loads(response.read().decode())
                        if result.get("success"):
                            return True
                        elif "score" in result:
                            score = result.get("score")
                            if score and float(score) >= 0.5:
                                return True
                            else:
                                st.error(f"Debug: Low Score ({score})")
                                return False
                        if not result.get("success"):
                            st.error(f"Debug: Verification Failed. Google Response: {result}")
                            return False
                        return False
                except Exception as e:
                    st.error(f"reCAPTCHA Verification Error: {e}")
                    return False

            if submit_btn:
                is_human = verify_recaptcha_token(recaptcha_token)
                if not is_human:
                    if not recaptcha_token:
                        st.error("reCAPTCHAのチェックボックスをオンにしてください。ページをリロードして再試行してください。")
                    else:
                        st.error("reCAPTCHA認証に失敗しました。")
                elif not is_valid_email:
                    st.error("正しいメールアドレスの形式で入力してください。")
                elif name and email and grade and desired_dept and strengthen_subjects and subject:
                    message_with_time = f"【面談希望時間】{preferred_time}\n\n{message}" if message else f"【面談希望時間】{preferred_time}"
                    sheet_saved = save_to_sheet(name, email, grade, desired_dept, strengthen_subjects, subject, message_with_time, date)
                    if sheet_saved:
                        st.success("✅ お申し込みありがとうございます！担当の政経生講師より2営業日以内にご連絡いたします。")
                    else:
                        st.error("送信に失敗しました。しばらく時間をおいて再度お試しください。")
                else:
                    st.error("全ての必須項目を入力してください。")



# ─────────────────────────────────────────
# 4. Main App Layout
# ─────────────────────────────────────────

def main():
    inject_scroll_preservation()

    hero_section()
    pain_points_section()

    st.divider()
    features_section()

    st.divider()
    flow_section()

    st.divider()
    instructors_section()

    st.divider()
    comparison_section()

    pricing_section()

    st.divider()
    faq_section()

    contact_section()

    # Footer
    st.markdown("""
        <div style="text-align:center;margin-top:5rem;padding:2.5rem 1rem;color:#9CA3AF;
                    border-top:1px solid #E5E7EB;font-size:0.85rem;">
            <p style="font-weight:700;color:#6B7280;margin-bottom:0.5rem;">Gakuin Tutor</p>
            <p style="margin-bottom:0.25rem;">&copy; 2026 Gakuin Tutor. All rights reserved.</p>
            <p style="margin-bottom:1rem;">※ 本サービスは早稲田大学高等学院の公式サービスではありません。</p>
            <details style="display:inline-block;text-align:left;max-width:560px;
                            background:#F3F4F6;border-radius:10px;padding:0.75rem 1.25rem;
                            border:1px solid #E5E7EB;font-size:0.78rem;color:#6B7280;">
                <summary style="cursor:pointer;font-weight:700;color:#4B5563;
                                list-style:none;display:flex;align-items:center;gap:0.5rem;">
                    📋 特定商取引法に基づく表記
                </summary>
                <table style="width:100%;margin-top:0.75rem;border-collapse:collapse;
                              font-size:0.78rem;line-height:1.8;">
                    <tr>
                        <td style="padding:0.3rem 0.75rem 0.3rem 0;font-weight:700;
                                   white-space:nowrap;vertical-align:top;color:#4B5563;">運営者</td>
                        <td style="padding:0.3rem 0;color:#6B7280;">早大学院生専用家庭教師 事務局</td>
                    </tr>
                    <tr>
                        <td style="padding:0.3rem 0.75rem 0.3rem 0;font-weight:700;
                                   white-space:nowrap;vertical-align:top;color:#4B5563;">対価</td>
                        <td style="padding:0.3rem 0;color:#6B7280;">各プランに記載の月額料金の通り（税込）</td>
                    </tr>
                    <tr>
                        <td style="padding:0.3rem 0.75rem 0.3rem 0;font-weight:700;
                                   white-space:nowrap;vertical-align:top;color:#4B5563;">支払時期</td>
                        <td style="padding:0.3rem 0;color:#6B7280;">前払い制（当月分を前月末日までにお支払いください）</td>
                    </tr>
                    <tr>
                        <td style="padding:0.3rem 0.75rem 0.3rem 0;font-weight:700;
                                   white-space:nowrap;vertical-align:top;color:#4B5563;">返金・<br>キャンセル</td>
                        <td style="padding:0.3rem 0;color:#6B7280;">
                            サービスの性質上、指導実施後の返金は承りかねます。<br>
                            退会は前月15日までにお申し出いただければ、翌月より解約となります。
                        </td>
                    </tr>
                    <tr>
                        <td style="padding:0.3rem 0.75rem 0.3rem 0;font-weight:700;
                                   white-space:nowrap;vertical-align:top;color:#4B5563;">お問合せ</td>
                        <td style="padding:0.3rem 0;color:#6B7280;">本サイトのお問い合わせフォームよりご連絡ください。</td>
                    </tr>
                </table>
            </details>
        </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
