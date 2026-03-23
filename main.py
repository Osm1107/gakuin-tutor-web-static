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
# --- Custom Component Declaration ---
# This allows us to receive data (token) from the frontend via postMessage
try:
    recaptcha_component = components.declare_component(
        "recaptcha_component",
        path="recaptcha_component"
    )
except Exception:
    # Fallback if path not found during dev or strange reload
    recaptcha_component = None

st.set_page_config(
    page_title="早大学院生専用家庭教師",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. Design System & Custom CSS ---
def local_css():
    st.markdown("""
    <style>
        /* Import Google Fonts */
        @import url('https://fonts.googleapis.com/css2?family=Noto+Serif+JP:wght@400;700;900&family=Noto+Sans+JP:wght@400;500;700&display=swap');

        :root {
            --waseda-red: #8E2034;
            --waseda-red-light: #B02E48;
            --bg-gray: #F9FAFB;
            --text-dark: #1F2937;
            --text-gray: #4B5563;
            --white: #FFFFFF;
        }

        /* General Reset & Typography */
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
        
        strong {
            color: var(--waseda-red);
            font-weight: 700;
        }

        /* Hide Streamlit Branding */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}

        /* --- Components --- */

        /* Hero Section */
        .hero-container {
            background: linear-gradient(135deg, var(--waseda-red) 0%, #5e1121 100%);
            color: white;
            padding: 6rem 2rem;
            text-align: center;
            border-radius: 0 0 50px 50px;
            margin-bottom: 4rem;
            box-shadow: 0 10px 30px -10px rgba(142, 32, 52, 0.5);
        }
        .hero-title {
            font-size: 3.5rem;
            font-weight: 900;
            margin-bottom: 1.5rem;
            line-height: 1.2;
            color: white !important;
        }
        .hero-subtitle {
            font-size: 1.25rem;
            margin-bottom: 2.5rem;
            opacity: 0.9;
        }
        
        /* Buttons */
        div.stButton > button {
            background-color: var(--waseda-red);
            color: white !important;
            border: none;
            padding: 0.75rem 2rem;
            font-size: 1.1rem;
            font-weight: 700;
            border-radius: 50px;
            transition: all 0.3s ease;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        div.stButton > button:hover {
            background-color: var(--waseda-red-light);
            transform: translateY(-2px);
            box-shadow: 0 10px 15px rgba(0,0,0,0.1);
            color: white !important;
        }
        div.stButton > button:active {
            transform: translateY(0);
        }

        /* Secondary Button (Outline) */
        .btn-outline {
            border: 2px solid white;
            background: transparent;
        }

        /* Section Styling */
        .section-header {
            text-align: center;
            margin-bottom: 3rem;
        }
        .section-header h2 {
            font-size: 2.5rem;
            margin-bottom: 1rem;
            display: inline-block;
            border-bottom: 4px solid var(--waseda-red);
            padding-bottom: 0.5rem;
        }

        /* Cards */
        .card {
            background: white;
            padding: 2rem;
            border-radius: 20px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            height: 100%;
            border: 1px solid #f0f0f0;
        }
        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
        }
        .card-icon {
            font-size: 5rem;
            margin-bottom: 1rem;
            color: var(--waseda-red);
            line-height: 1;
            text-align: center;
        }
        .card-title {
            font-size: 1.25rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
        }
        
        /* Instructor Profile */
        .profile-img-placeholder {
            width: 120px;
            height: 120px;
            background-color: #eee;
            border-radius: 50%;
            margin: 0 auto 1.5rem auto;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 2rem;
            color: #aaa;
            border: 4px solid var(--waseda-red);
        }
        
        /* Contact Form */
        .stTextInput > div > div > input, .stTextArea > div > div > textarea {
            border-radius: 10px;
            border: 1px solid #e5e7eb;
            padding: 10px;
        }
        .stTextInput > div > div > input:focus, .stTextArea > div > div > textarea:focus {
            border-color: var(--waseda-red);
            box-shadow: 0 0 0 1px var(--waseda-red);
        }

        /* Grid Layout for Pain Points */
        .pain-points-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 1.5rem;
            margin-bottom: 2rem;
        }
        
        @media (max-width: 768px) {
            .pain-points-grid {
                grid-template-columns: 1fr;
            }
        }

    </style>
    """, unsafe_allow_html=True)

local_css()

# --- Scroll Preservation ---
# --- Scroll Preservation ---
def inject_scroll_preservation():
    components.html(
        """
        <script>
            var attempts = 0;
            var maxAttempts = 20; // Try for 2 seconds
            var targetScroll = sessionStorage.getItem('scrollPosition');
            
            if (targetScroll) {
                targetScroll = parseInt(targetScroll);
                var restoreInterval = setInterval(function() {
                    if (window.parent) {
                        var currentScroll = window.parent.scrollY;
                        var docHeight = window.parent.document.body.scrollHeight;
                        
                        // Try to scroll
                        window.parent.scrollTo(0, targetScroll);
                        
                        // Check if we made it (approximate) or if document is still short
                        if (Math.abs(window.parent.scrollY - targetScroll) < 10 || attempts >= maxAttempts) {
                            clearInterval(restoreInterval);
                        }
                        attempts++;
                    } else {
                        clearInterval(restoreInterval);
                    }
                }, 100);
            }

            // Saving scroll position
            if (window.parent) {
                window.parent.addEventListener('scroll', function() {
                    sessionStorage.setItem('scrollPosition', window.parent.scrollY);
                });
            }
        </script>
        """,
        height=0,
    )


# --- 3. Component Functions & Logic ---

def send_email(name, user_email, grade, desired_dept, strengthen_subjects, subject, message):
    try:
        # Load secrets
        sender_email = st.secrets["email"]["address"]
        sender_password = st.secrets["email"]["password"]
        receiver_email = sender_email # Send to self

        # Create message
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = receiver_email
        msg['Subject'] = f"【Gakuin Tutor】新規お問い合わせ: {name}様"

        # Format subjects list
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

        # Send email via Gmail server
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        text = msg.as_string()
        server.sendmail(sender_email, receiver_email, text)
        server.quit()
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
        
        # Parse JSON response to get debug log
        try:
            result = response.json()
            if "debug_log" in result:
                st.info(f"GAS Debug Log: {result['debug_log']}")
            
            # Check for logical error returned by GAS (even if HTTP 200)
            if result.get("status") == "error":
                 st.error(f"GAS Logic Error: {result.get('message')}")
                 return False

        except:
             # Fallback if response isn't JSON (e.g. HTML error page)
             pass

        # Debug: Show detailed response from GAS if failed
        if response.status_code != 200:
            st.error(f"GAS Error ({response.status_code}): {response.text}")
        
        if response.status_code == 200:
            return True
        else:
            return False
    except Exception as e:
        st.error(f"Connection Error: {e}")
        return False

def hero_section():
    st.markdown("""
        <div class="hero-container">
            <h1 class="hero-title">学院の評定、<br>学院の先輩に頼ろう。</h1>
            <p class="hero-subtitle">
                早稲田大学高等学院生専門オンライン家庭教師サービス。<br>
                内部進学の不安を、同じ道を歩んだ先輩が解消します。
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # Call to Action placed centrally using columns for better layout control
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("無料相談に申し込む", key="hero_cta", use_container_width=True):
            js = '''
            <script>
                var element = window.parent.document.getElementById("contact-form");
                if (element) {
                    element.scrollIntoView({behavior: "smooth", block: "start"});
                } else {
                    // Fallback for some iframe structures or if ID inside iframe
                    // Actually streamlit components are in iframes, so getting element from parent might be tricky
                    // if the target is in the main parent document.
                    // Streamlit renders everything in one document usually, but components are iframes.
                    // To scroll main page from component:
                    window.parent.document.getElementById("contact-form").scrollIntoView({behavior: "smooth"});
                }
            </script>
            '''
            # Simple script to scroll to element with ID 'contact-form' in the parent document
            # because streamlit components run in an iframe.
            components.html(f"""
                <script>
                    window.parent.document.getElementById('contact-form').scrollIntoView({{behavior: 'smooth'}});
                </script>
            """, height=0)

def get_image_as_base64(file_path):
    with open(file_path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

def pain_points_section():
    st.markdown('<div class="section-header"><h2>こんな悩み、ありませんか？</h2></div>', unsafe_allow_html=True)
    
    try:
        icon_b64 = get_image_as_base64("pronunciation_icon.png")
        # Set width/height to 80px to match roughly 5rem font size of emojis
        icon_html = f'<img src="data:image/png;base64,{icon_b64}" style="width: 80px; height: 80px; object-fit: contain; margin-bottom: 1rem;">'
    except Exception:
        icon_html = '<div class="card-icon">🇩🇪🇨🇳</div>'

    st.markdown(f"""
        <div class="pain-points-grid">
            <div class="card">
                <div style="text-align: center;">{icon_html}</div>
                <div class="card-title">第二外国語が鬼門...</div>
                <p>ドイツ語・中国語・フランス語・ロシア語。<br>
                進級・卒業にかかわる重要科目なのに、対策できる塾がない。</p>
            </div>
            <div class="card">
                <div class="card-icon">⚖️</div>
                <div class="card-title">政経進学のボーダー</div>
                <p>人気の政治経済学部への内部進学。<br>
                評定を1点でも上げるための戦略的な定期テスト対策がしたい。</p>
            </div>
            <div class="card">
                <div class="card-icon">🎓</div>
                <div class="card-title">進路・学部選びの不安</div>
                <p>「実際のキャンパスライフは？」<br>
                パンフレットにはないリアルな情報を、<strong>現役の早大生</strong>が教えます。</p>
            </div>
        </div>
    """, unsafe_allow_html=True)
    st.markdown("<br><br>", unsafe_allow_html=True)

def features_section():
    st.markdown('<div class="section-header"><h2>我々の強み</h2></div>', unsafe_allow_html=True)
    
    # Feature Layout
    col1, col2 = st.columns(2, gap="large")

    # Feature 1 (Left Column)
    with col1:
        st.markdown("""
        <div style="padding: 10px; height: 100%; display: flex; flex-direction: column;">
            <h3 style="white-space: nowrap;">🎓 講師は全員「学院出身」の早大生</h3>
            <p style="font-size: 1.1rem; line-height: 1.8; flex-grow: 1;">
                一般の塾講師では理解できない<strong>「学院独自のカリキュラム」</strong>や
                <strong>「先生ごとの出題傾向」</strong>を完全に把握しています。<br>
                あなたの今の悩みは、先輩が数年前に乗り越えた道です。
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        try:
            campus_img_b64 = get_image_as_base64("waseda_classroom_new.jpg")
            st.markdown(f'<img src="data:image/png;base64,{campus_img_b64}" style="width: 100%; aspect-ratio: 1 / 1; object-fit: cover; border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-top: 1rem;">', unsafe_allow_html=True)
        except Exception:
            st.image("https://images.unsplash.com/photo-1523240795612-9a054b0db644?auto=format&fit=crop&q=80&w=800", caption="同じキャンパスを知る先輩が伴走します", use_container_width=True)

    # Feature 2 (Right Column)
    with col2:
        st.markdown("""
        <div style="padding: 10px; height: 100%; display: flex; flex-direction: column;">
            <h3 style="white-space: nowrap;">📊 徹底的な定期テスト・レポート対策</h3>
            <p style="font-size: 1.1rem; line-height: 1.8; flex-grow: 1;">
                学院の評定は、日々の積み重ねで決まります。<br>
                なんとなくの勉強ではなく、<strong>「評定を取るための勉強」</strong>へ。<br>
                過去の傾向分析に基づき、効率よく点数を最大化します。
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        try:
            study_img_b64 = get_image_as_base64("waseda_okuma_statue.jpg")
            st.markdown(f'<img src="data:image/png;base64,{study_img_b64}" style="width: 100%; aspect-ratio: 1 / 1; object-fit: cover; border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-top: 1rem;">', unsafe_allow_html=True)
        except Exception:
            st.image("https://images.unsplash.com/photo-1434030216411-0b793f4b4173?auto=format&fit=crop&q=80&w=800", caption="戦略的な学習計画を提案", use_container_width=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)

def instructors_section():
    st.markdown('<div class="section-header"><h2>自慢の講師陣</h2><p>政経・商・国教・理工など、各学部の上位進学者が在籍</p></div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    instructors = [
        {"name": "K.S 先輩", "dept": "政治経済学部 経済学科", "strength": "数学・ドイツ語", "desc": "高3で評定85点をキープし政経へ。"},
        {"name": "T.M 先輩", "dept": "商学部", "strength": "英語・数学", "desc": "特考の平均が9。"},
        {"name": "Y.O 先輩", "dept": "創造理工学部", "strength": "物理・化学", "desc": "理系科目のエキスパート。"},
        {"name": "H.A 先輩", "dept": "商学部", "strength": "英語・中国語", "desc": "中国語検定取得済み。"},
    ]
    
    cols = [col1, col2, col3, col4]
    
    for i, inst in enumerate(instructors):
        with cols[i]:
            st.markdown(f"""
                <div class="card" style="text-align: center; padding: 1.5rem;">
                    <div class="profile-img-placeholder">👨‍🎓</div>
                    <div class="card-title">{inst['name']}</div>
                    <div style="color: var(--waseda-red); font-weight:bold; font-size: 0.9rem; margin-bottom: 0.5rem;">{inst['dept']}</div>
                    <p style="font-size: 0.9rem;"><strong>得意:</strong> {inst['strength']}</p>
                    <p style="font-size: 0.85rem; color: #666;">{inst['desc']}</p>
                </div>
            """, unsafe_allow_html=True)
    st.markdown("<br><br>", unsafe_allow_html=True)

def pricing_section():
    st.markdown("""
        <div style="background-color: var(--waseda-red); color: white; padding: 3rem; border-radius: 20px; text-align: center; margin-bottom: 4rem;">
            <h2 style="color: white; border-bottom: none;">シンプルな料金プラン</h2>
            <p style="margin-bottom: 2rem;">入会金・教材費は一切かかりません。</p>
            <div style="background: white; color: var(--text-dark); max-width: 600px; margin: 0 auto; padding: 2rem; border-radius: 15px; box-shadow: 0 10px 25px rgba(0,0,0,0.2);">
                <h3 style="margin-bottom: 0;">スタンダードプラン</h3>
                <div style="font-size: 3rem; font-weight: 900; color: var(--waseda-red); margin: 1rem 0;">
                    ¥4,000 <span style="font-size: 1rem; color: var(--text-gray); font-weight: 400;">/ 1時間</span>
                </div>
                <ul style="text-align: left; margin-bottom: 2rem; list-style: none; padding: 0 2rem;">
                    <li style="margin-bottom: 10px;">✅ 週1回〜 お好きな頻度で受講可能</li>
                    <li style="margin-bottom: 10px;">✅ 全科目対応（第二外国語含む）</li>
                    <li style="margin-bottom: 10px;">✅ LINEでの質問サポート付き</li>
                    <li style="margin-bottom: 10px;">✅ 卒論・レポート添削も同料金</li>
                </ul>
            </div>
        </div>
    """, unsafe_allow_html=True)

def contact_section():
    st.markdown('<div id="contact-form" class="section-header"><h2>無料相談のお申し込み</h2><p>まずは現状の評定やお悩みをお聞かせください。<br>あなたにぴったりの学習プランをご提案します。</p></div>', unsafe_allow_html=True)
    
    with st.form("contact_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("お名前 (必須)")
            email = st.text_input("メールアドレス (必須)")
            grade = st.selectbox("学年 (必須)", ["中学1年生", "中学2年生", "中学3年生", "高校1年生", "高校2年生", "高校3年生"])
        with col2:
            desired_dept = st.selectbox("志望学部 (必須)", [
                "政治経済学部", "法学部", "商学部", "社会科学部", "教育学部", 
                "文学部", "文化構想学部", "基幹理工学部", "創造理工学部", 
                "先進理工学部", "人間科学部", "スポーツ科学部", "未定"
            ])
            strengthen_subjects = st.multiselect("特に強化したい科目 (複数選択可・必須)", [
                "英語", "数学", "国語", "理科（物理・化学・生物）", 
                "社会（地歴・公民）", "第二外国語（ドイツ語・フランス語・ロシア語・中国語）"
            ])
            subject = st.text_input("相談したい件名・内容 (必須)", placeholder="例：定期テスト対策について、進路相談など")
            date = st.date_input("体験希望日時", min_value=datetime.date.today())
        
        message = st.text_area("詳細なご相談内容", height=150)
        
        # Render reCAPTCHA widget using Custom Component
        site_key = st.secrets["recaptcha"]["site_key"]
        
        # The component returns the value passed to setComponentValue() in JS
        # Default is None until the user interactions sends data
        recaptcha_token = recaptcha_component(site_key=site_key, key="recaptcha")
        
        # Debug helper (remove in production if needed, or keep for user assurance)
        # if recaptcha_token:
        #     st.caption("reCAPTCHA Token Received")


        # Server-side Verification Logic
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
                    
                    # Handle both v2 (success: true) and v3/Enterprise (score)
                    if result.get("success"):
                        return True
                    elif "score" in result:
                        score = result.get("score")
                        if score and float(score) >= 0.5:
                            return True
                        else:
                            st.error(f"Debug: Low Score ({score})")
                            return False
                    
                    # Debug: Show error details to user for troubleshooting
                    if not result.get("success"):
                        st.error(f"Debug: Verification Failed. Google Response: {result}")
                        return False
                    return False
            except Exception as e:
                st.error(f"reCAPTCHA Verification Error: {e}")
                return False

        submit_btn = st.form_submit_button("送信する", use_container_width=True)

        st.markdown("""
<div style="margin-top: 20px; margin-bottom: 30px; font-size: 11px; color: #777777; line-height: 1.6;">
    <p style="text-align: center; margin-bottom: 15px;">送信ボタンを押すことで、以下のプライバシーポリシーに同意したものとみなされます。</p>
    <div style="text-align: left; padding: 15px; background-color: #f9f9f9; border-radius: 8px;">
        <p style="font-weight: bold; margin-bottom: 10px;">【プライバシーポリシー】</p>
        <p style="margin-bottom: 10px;">早大学院生専用家庭教師 事務局（以下、「当方」といいます。）は、本ウェブサイト上で提供するサービス（以下、「本サービス」といいます。）における、ユーザーの個人情報の取扱いについて、以下のとおりプライバシーポリシー（以下、「本ポリシー」といいます。）を定めます。</p>
        <p style="margin-bottom: 5px;"><strong>第1条（個人情報）</strong></p>
        <p style="margin-bottom: 10px;">「個人情報」とは、個人情報保護法にいう「個人情報」を指すものとし、生存する個人に関する情報であって、当該情報に含まれる氏名、連絡先（メールアドレス等）、学年、志望学部、学習状況、その他の記述等により特定の個人を識別できる情報を指します。</p>
        <p style="margin-bottom: 5px;"><strong>第2条（個人情報の収集・利用目的）</strong></p>
        <p style="margin-bottom: 5px;">当方が個人情報を収集・利用する目的は、以下のとおりです。</p>
        <ol style="margin-bottom: 10px; padding-left: 20px;">
            <li>体験授業および指導の日程調整のため</li>
            <li>お問い合わせへの回答および連絡のため（自動返信メールを含む）</li>
            <li>生徒様の学習状況に合わせた指導カリキュラム作成のため</li>
            <li>不正・不当な目的でサービスを利用しようとするユーザーの特定をし、ご利用をお断りするため</li>
        </ol>
        <p style="margin-bottom: 5px;"><strong>第3条（個人情報の管理・セキュリティ）</strong></p>
        <p style="margin-bottom: 10px;">当方は、お預かりした個人情報を正確かつ最新の状態に保ち、個人情報への不正アクセス・紛失・破損・改ざん・漏洩などを防止するため、セキュリティシステムの維持・管理体制の整備等の必要な措置を講じます。<br>
        なお、日程調整および顧客管理においては、高度なセキュリティ基準を有するGoogle社が提供するクラウドサービス（Google Workspace等）を利用し、厳重に管理を行っております。</p>
        <p style="margin-bottom: 5px;"><strong>第4条（第三者提供の禁止）</strong></p>
        <p style="margin-bottom: 5px;">当方は、次に掲げる場合を除いて、あらかじめユーザーの同意を得ることなく、第三者に個人情報を提供することはありません。</p>
        <ol style="margin-bottom: 10px; padding-left: 20px;">
            <li>人の生命、身体または財産の保護のために必要がある場合であって、本人の同意を得ることが困難であるとき</li>
            <li>公衆衛生の向上または児童の健全な育成の推進のために特に必要がある場合であって、本人の同意を得ることが困難であるとき</li>
            <li>法令に基づき開示することが必要である場合</li>
        </ol>
        <p style="margin-bottom: 5px;"><strong>第5条（個人情報の開示・訂正・削除）</strong></p>
        <p style="margin-bottom: 10px;">ユーザーがご本人の個人情報の開示・訂正・追加・削除・利用停止などを希望される場合には、ご本人であることを確認の上、速やかに対応いたします。</p>
        <p style="margin-bottom: 5px;"><strong>第6条（お問い合わせ窓口）</strong></p>
        <p style="margin-bottom: 0;">本ポリシーに関するお問い合わせは、本ウェブサイトのお問い合わせフォームよりお願いいたします。</p>
    </div>
</div>
""", unsafe_allow_html=True)
        
        # Validate Email
        import re
        email_pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        is_valid_email = re.match(email_pattern, email) is not None

        if submit_btn:
            # Perform verification
            is_human = verify_recaptcha_token(recaptcha_token)
            
            # Since auto-reload isn't guaranteed, we might check if token is missing but user clicked submit
            # For this code to work strictly as requested:
            if not is_human:
                 # If token is missing (common without library), we show a helpful message or strict error
                 # Per user request: "Fail if verify checks fails"
                 if not recaptcha_token:
                    st.error("reCAPTCHAのチェックボックスをオンにしてください（※認証トークンが取得できませんでした。ページをリロードして再試行してください）。")
                 else:
                    st.error("reCAPTCHA認証に失敗しました。")
            elif not is_valid_email:
                 st.error("正しいメールアドレスの形式で入力してください。")
            elif name and email and grade and desired_dept and strengthen_subjects and subject:
                # Reset captcha on success (optional, but good for fresh state next time)
                # But tricky inside form submit. Usually reset after success action.
                pass 
                
                # Try to send email (Deprecated: Now using Slack via GAS)
                # email_sent = send_email(name, email, grade, desired_dept, strengthen_subjects, subject, message)
                
                # Try to save to Google Sheet (Primary success indicator & Slack Notification)
                sheet_saved = save_to_sheet(name, email, grade, desired_dept, strengthen_subjects, subject, message, date)
                
                if sheet_saved:
                    st.success("お申し込みありがとうございます。確認メールをお送りしました。")
                    # Email notification removed in favor of Slack
                    # if not email_sent:
                    #     print("Warning: Email could not be sent, but data was saved to sheet.")
                # elif email_sent:
                     # Fallback if sheet fails but email works (unlikely case but good to handle)
                #     st.success("お問い合わせありがとうございます！内容が送信されました。担当者よりご連絡いたします。")
                else:
                    st.error("送信に失敗しました。しばらく時間を置いて再度お試しください。")
            else:
                st.error("全ての項目を入力してください。")

# --- 4. Main App Layout ---

def main():
    # Inject scroll preservation script
    inject_scroll_preservation()

    # Render sections
    hero_section()
    
    # Container for main content to add side margins on wide screens if needed, 
    # though Streamlit layout="wide" handles this well.
    
    pain_points_section()
    
    st.divider()
    
    features_section()
    
    st.divider()
    
    instructors_section()
    
    pricing_section()
    
    contact_section()

    # Footer
    st.markdown("""
        <div style="text-align: center; margin-top: 5rem; padding: 2rem; color: #888; border-top: 1px solid #eee;">
            <p>&copy; 2026 Gakuin Tutor. All rights reserved.</p>
            <p style="font-size: 0.8rem;">※本サービスは早稲田大学高等学院の公式サービスではありません。</p>
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
