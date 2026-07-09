import streamlit as st
import database
import os
import fitz
import json
import extra_streamlit_components as stx
from datetime import datetime, timedelta

# Helper to render PDF pages to images
def render_pdf_to_images(pdf_path):
    images = []
    try:
        doc = fitz.open(pdf_path)
        for page in doc:
            pix = page.get_pixmap(dpi=130)  # Render page to standard resolution
            img_bytes = pix.tobytes("png")
            images.append(img_bytes)
        doc.close()
    except Exception as e:
        print(f"Error rendering PDF pages to images: {e}")
    return images

# Set page configurations
st.set_page_config(
    page_title="Vibe Coding All-in-One Platform",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom premium styling using CSS
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&family=Noto+Sans+KR:wght@300;400;500;700&display=swap');

/* Apply modern typography */
html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
    font-family: 'Outfit', 'Noto Sans KR', sans-serif;
    background-color: #0f172a;
    color: #f8fafc;
}

/* Improve widget label visibility */
[data-testid="stWidgetLabel"] p,
[data-testid="stWidgetLabel"],
.stTextInput label,
.stTextArea label,
.stSelectbox label,
.stCheckbox label,
.stFileUploader label,
.stSlider label,
.stRadio label,
[data-baseweb="label"],
[data-baseweb="checkbox"] span {
    color: #e2e8f0 !important;
    font-size: 0.97rem !important;
    font-weight: 500 !important;
}

/* Selectbox option text color */
[data-baseweb="select"] div {
    color: #f1f5f9 !important;
    background-color: #1e293b !important;
}
[data-baseweb="select"] div[data-testid="stSelectboxVirtualDropdown"] li {
    color: #e2e8f0 !important;
}

/* Expander header */
[data-testid="stExpander"] summary p {
    color: #c7d2fe !important;
    font-size: 0.97rem !important;
    font-weight: 600 !important;
}

/* Sidebar Customization */
[data-testid="stSidebar"] {
    background-color: #1e293b;
    border-right: 1px solid #334155;
}

/* Sidebar button nav styles */
[data-testid="stSidebar"] .nav-btn-wrapper > div {
    margin-bottom: 0.35rem;
}
[data-testid="stSidebar"] .nav-btn-wrapper button {
    background: transparent;
    border: 1px solid transparent;
    color: #94a3b8;
    font-size: 1.05rem;
    font-weight: 500;
    font-family: 'Outfit', 'Noto Sans KR', sans-serif;
    text-align: left;
    border-radius: 8px;
    padding: 0.6rem 0.9rem;
    transition: all 0.18s ease;
    width: 100%;
    cursor: pointer;
}
[data-testid="stSidebar"] .nav-btn-wrapper button:hover {
    background: rgba(99,102,241,0.12);
    border-color: #6366f1;
    color: #c7d2fe;
    transform: translateX(3px);
}
[data-testid="stSidebar"] .nav-btn-wrapper button.active-nav {
    background: linear-gradient(135deg, rgba(99,102,241,0.25), rgba(139,92,246,0.15));
    border-color: #6366f1;
    color: #a5b4fc;
    font-weight: 700;
    box-shadow: 0 2px 8px rgba(99,102,241,0.2);
}
.sidebar-section-label {
    font-size: 0.72rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: #475569;
    padding: 0.75rem 0.5rem 0.35rem;
    margin-top: 0.5rem;
}

/* Title Area Styles */
.title-container {
    background: linear-gradient(135deg, #1e1b4b 0%, #0f172a 100%);
    padding: 2.5rem;
    border-radius: 16px;
    border: 1px solid #312e81;
    margin-bottom: 2.5rem;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
}

.main-title {
    font-size: 2.8rem;
    font-weight: 700;
    background: linear-gradient(135deg, #a78bfa 0%, #818cf8 50%, #60a5fa 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0.5rem;
}

.sub-title {
    font-size: 1.1rem;
    color: #94a3b8;
    margin-bottom: 0;
}

/* Custom premium card design */
.qna-card {
    background-color: #1e293b;
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 1.5rem;
    border: 1px solid #334155;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    transition: transform 0.2s, border-color 0.2s;
}

.qna-card:hover {
    transform: translateY(-2px);
    border-color: #6366f1;
}

.question-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid #334155;
    padding-bottom: 0.75rem;
    margin-bottom: 0.75rem;
}

.question-author {
    font-weight: 600;
    color: #f8fafc;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.question-date {
    font-size: 0.85rem;
    color: #64748b;
}

.question-body {
    font-size: 1rem;
    color: #e2e8f0;
    white-space: pre-wrap;
    margin-bottom: 1rem;
    line-height: 1.5;
}

.answer-section {
    background-color: #0f172a;
    border-left: 4px solid #10b981;
    border-radius: 4px;
    padding: 1rem;
    margin-top: 1rem;
}

.answer-header {
    font-weight: 600;
    color: #34d399;
    font-size: 0.9rem;
    margin-bottom: 0.5rem;
}

.answer-body {
    font-size: 0.95rem;
    color: #cbd5e1;
    white-space: pre-wrap;
    line-height: 1.5;
}

.answer-pending {
    font-size: 0.85rem;
    color: #f59e0b;
    font-style: italic;
    background-color: rgba(245, 158, 11, 0.1);
    padding: 0.5rem 1rem;
    border-radius: 4px;
    display: inline-block;
}

/* Badges */
.role-badge {
    padding: 0.2rem 0.6rem;
    border-radius: 9999px;
    font-size: 0.75rem;
    font-weight: 700;
    display: inline-block;
}

.role-admin {
    background: linear-gradient(135deg, #d97706 0%, #f59e0b 100%);
    color: #ffffff;
}

.role-student {
    background: linear-gradient(135deg, #2563eb 0%, #3b82f6 100%);
    color: #ffffff;
}

/* Global status banner */
.user-status-banner {
    background-color: #1e293b;
    padding: 0.75rem 1.5rem;
    border-radius: 8px;
    border-left: 4px solid #6366f1;
    margin-bottom: 2rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
}
</style>
""", unsafe_allow_html=True)

# ── Cookie-based session persistence ─────────────────────────────────────────
cookie_manager = stx.CookieManager(key="vibe_cookie_manager")

# Initialize Session State
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_info" not in st.session_state:
    st.session_state.user_info = None
if "edit_mode" not in st.session_state:
    st.session_state.edit_mode = False
if "selected_chapter_id" not in st.session_state:
    st.session_state.selected_chapter_id = "1"
if "menu" not in st.session_state:
    st.session_state.menu = "🔓 로그인 / 회원가입"
if "_force_logged_out" not in st.session_state:
    st.session_state._force_logged_out = False

# Restore session from cookies on page refresh
# Skip restore if the user explicitly logged out this session
if not st.session_state.logged_in and not st.session_state._force_logged_out:
    try:
        session_cookie = cookie_manager.get("vibe_session")
        if session_cookie:
            saved = json.loads(session_cookie)
            users = database.load_users()
            uname = saved.get("username", "")
            if uname in users:
                st.session_state.logged_in = True
                u = users[uname]
                st.session_state.user_info = {
                    "username": uname,
                    "name": u.get("name", uname),
                    "is_admin": u.get("is_admin", False)
                }
    except Exception:
        pass

# ── Sidebar ───────────────────────────────────────────────────────────────────
st.sidebar.markdown("""
<div style="padding: 1.25rem 0.5rem 0.25rem; display: flex; align-items: center; gap: 0.6rem;">
    <span style="font-size: 2rem;">🎓</span>
    <div>
        <div style="font-size: 1.2rem; font-weight: 800; background: linear-gradient(135deg, #a78bfa, #60a5fa); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">Vibe Learning</div>
        <div style="font-size: 0.75rem; color: #64748b;">바이브 코딩 올인원 플랫폼</div>
    </div>
</div>
<hr style="border-color: #1e293b; margin: 0.75rem 0;">
""", unsafe_allow_html=True)

# Show logged-in user card
if st.session_state.logged_in:
    role_label = "관리자" if st.session_state.user_info['is_admin'] else "교육생"
    role_class = "role-admin" if st.session_state.user_info['is_admin'] else "role-student"
    st.sidebar.markdown(f"""
    <div style="background-color: #0f172a; padding: 0.85rem 1rem; border-radius: 10px; border: 1px solid #334155; margin-bottom: 0.5rem;">
        <div style="font-size: 0.75rem; color: #64748b; margin-bottom: 0.2rem;">접속 중</div>
        <div style="font-weight: 700; font-size: 1.05rem; color: #f1f5f9;">{st.session_state.user_info['name']}님</div>
        <span class="role-badge {role_class}" style="margin-top: 0.4rem;">{role_label}</span>
    </div>
    """, unsafe_allow_html=True)
else:
    st.sidebar.markdown("""
    <div style="background: rgba(99,102,241,0.08); border: 1px dashed #475569; padding: 0.75rem 1rem; border-radius: 8px; font-size: 0.88rem; color: #94a3b8; margin-bottom: 0.5rem;">
        🔒 로그인 후 모든 기능을 이용하실 수 있습니다.
    </div>
    """, unsafe_allow_html=True)

# ── Button-style navigation ───────────────────────────────────────────────────
st.sidebar.markdown('<div class="sidebar-section-label">📌 메뉴</div>', unsafe_allow_html=True)

MENU_ITEMS = [
    ("🔓 로그인 / 회원가입", "🔓 로그인 / 회원가입"),
    ("📖 커리큘럼 마스터 (학습 및 편집)", "📖 커리큘럼 마스터 (학습 및 편집)"),
    ("💬 실시간 1:1 질의응답 (Q&A)", "💬 실시간 1:1 질의응답 (Q&A)"),
]

# Admin-only menu items
if st.session_state.logged_in and st.session_state.user_info.get('is_admin'):
    MENU_ITEMS.append(("👥 회원 및 Q&A 관리 (Admin)", "👥 회원 및 Q&A 관리 (Admin)"))

st.sidebar.markdown('<div class="nav-btn-wrapper">', unsafe_allow_html=True)
for label, key in MENU_ITEMS:
    if st.sidebar.button(label, key=f"nav_{key}", use_container_width=True):
        st.session_state.menu = key
        st.rerun()
st.sidebar.markdown('</div>', unsafe_allow_html=True)

menu = st.session_state.menu

# Validate menu access: admin-only page guard
if menu == "👥 회원 및 Q&A 관리 (Admin)":
    if not (st.session_state.logged_in and st.session_state.user_info.get('is_admin')):
        menu = "🔓 로그인 / 회원가입"
        st.session_state.menu = menu

# Logout button at bottom of sidebar
st.sidebar.markdown('<hr style="border-color: #1e293b; margin: 1rem 0;">', unsafe_allow_html=True)
if st.session_state.logged_in:
    if st.sidebar.button("🔓 로그아웃", key="sidebar_logout", use_container_width=True):
        try:
            cookie_manager.delete("vibe_session")
        except Exception:
            pass
        st.session_state.logged_in = False
        st.session_state.user_info = None
        st.session_state.edit_mode = False
        st.session_state._force_logged_out = True
        st.session_state.menu = "🔓 로그인 / 회원가입"
        st.rerun()

# Header Section
st.markdown("""
<div class="title-container">
    <h1 class="main-title">비개발자용 바이브 코딩 올인원 교육 플랫폼</h1>
    <p class="sub-title">AI 협업 코딩 학습 및 콘텐츠 실시간 관리 포탈</p>
</div>
""", unsafe_allow_html=True)


# --- PAGE 1: 로그인 / 회원가입 ---
if menu == "🔓 로그인 / 회원가입":
    st.subheader("🔓 계정 로그인 및 회원가입")
    
    if st.session_state.logged_in:
        st.success(f"현재 **{st.session_state.user_info['name']}**님 계정으로 로그인되어 있습니다.")
        
        # User details card
        is_admin_str = "관리자 권한 보유" if st.session_state.user_info['is_admin'] else "교육생 권한"
        st.markdown(f"""
        <div class="qna-card">
            <h3>내 프로필</h3>
            <p><strong>아이디:</strong> {st.session_state.user_info['username']}</p>
            <p><strong>성명:</strong> {st.session_state.user_info['name']}</p>
            <p><strong>권한:</strong> {is_admin_str}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Password Edit Form
        with st.expander("🔐 비밀번호 수정"):
            current_pw = st.text_input("현재 비밀번호", type="password", key="chg_curr_pw")
            new_pw = st.text_input("새 비밀번호", type="password", key="chg_new_pw")
            new_pw_confirm = st.text_input("새 비밀번호 확인", type="password", key="chg_new_pw_confirm")
            
            if st.button("비밀번호 변경 저장", key="save_pw_btn", use_container_width=True):
                users = database.load_users()
                username = st.session_state.user_info['username']
                hashed_curr = database.hash_password(current_pw)
                
                if not current_pw or not new_pw or not new_pw_confirm:
                    st.error("모든 항목을 입력해 주세요.")
                elif users[username]['password'] != hashed_curr:
                    st.error("현재 비밀번호가 올바르지 않습니다.")
                elif new_pw != new_pw_confirm:
                    st.error("새 비밀번호가 서로 일치하지 않습니다.")
                else:
                    users[username]['password'] = database.hash_password(new_pw)
                    database.save_users(users)
                    st.success("🔒 비밀번호가 성공적으로 변경되었습니다! 다음 로그인 시 변경된 비밀번호를 사용하세요.")
        
        st.write("")
        if st.button("로그아웃 하기", type="primary", use_container_width=True):
            try:
                cookie_manager.delete("vibe_session")
            except Exception:
                pass
            st.session_state.logged_in = False
            st.session_state.user_info = None
            st.session_state.edit_mode = False
            st.session_state._force_logged_out = True
            st.session_state.menu = "🔓 로그인 / 회원가입"
            st.rerun()
            
    else:
        tab_login, tab_register = st.tabs(["🔑 로그인", "📝 회원가입"])
        
        # Login Tab
        with tab_login:
            st.write("등록된 계정 정보를 입력하세요.")
            login_id = st.text_input("아이디", key="login_id_input")
            login_pw = st.text_input("비밀번호", type="password", key="login_pw_input")
            
            if st.button("로그인", key="login_submit_btn", type="primary"):
                if not login_id or not login_pw:
                    st.error("아이디와 비밀번호를 모두 입력해 주세요.")
                else:
                    users = database.load_users()
                    hashed = database.hash_password(login_pw)
                    if login_id in users and users[login_id]['password'] == hashed:
                        user_info = {
                            "username": login_id,
                            "name": users[login_id]['name'],
                            "is_admin": users[login_id].get('is_admin', False)
                        }
                        st.session_state.logged_in = True
                        st.session_state.user_info = user_info
                        st.session_state._force_logged_out = False  # Allow cookie restore next time
                        # Persist session in cookie (7-day expiry)
                        cookie_manager.set(
                            "vibe_session",
                            json.dumps({"username": login_id}),
                            expires_at=datetime.now() + timedelta(days=7)
                        )
                        st.success(f"환영합니다! {users[login_id]['name']}님 로그인 성공.")
                        st.session_state.menu = "📖 커리큘럼 마스터 (학습 및 편집)"
                        st.rerun()
                    else:
                        st.error("아이디 또는 비밀번호가 올바르지 않습니다.")
                        
        # Register Tab
        with tab_register:
            st.write("새로운 계정을 생성하세요. 아이디가 `admin`이거나 성명이 `관리자`이면 자동으로 관리자 권한이 부여됩니다.")
            reg_id = st.text_input("아이디 (최소 3자)", key="reg_id_input")
            reg_name = st.text_input("성명", key="reg_name_input")
            reg_pw = st.text_input("비밀번호", type="password", key="reg_pw_input")
            reg_pw_confirm = st.text_input("비밀번호 확인", type="password", key="reg_pw_confirm_input")
            
            if st.button("회원가입하기", key="reg_submit_btn"):
                users = database.load_users()
                
                if not reg_id or not reg_name or not reg_pw or not reg_pw_confirm:
                    st.error("모든 항목을 입력해 주세요.")
                elif len(reg_id) < 3:
                    st.error("아이디는 3자 이상이어야 합니다.")
                elif reg_pw != reg_pw_confirm:
                    st.error("비밀번호가 서로 일치하지 않습니다.")
                elif reg_id in users:
                    st.error("이미 존재하는 아이디입니다. 다른 아이디를 사용해 주세요.")
                else:
                    # Determine admin status:
                    # "아이디가 admin 이거나 성명이 관리자로 가입/로그인한 계정은 시스템에서 '관리자 권한'(is_admin = True)을 부여"
                    is_admin = (reg_id == "admin") or (reg_name == "관리자")
                    
                    # Store user details
                    users[reg_id] = {
                        "password": database.hash_password(reg_pw),
                        "name": reg_name,
                        "is_admin": is_admin
                    }
                    database.save_users(users)
                    st.success("회원가입이 완료되었습니다! 로그인 탭에서 로그인해 주세요.")


# --- PAGE 2: 커리큘럼 마스터 (조회 및 직접 수정 모듈) ---
elif menu == "📖 커리큘럼 마스터 (학습 및 편집)":
    # Login Guard
    if not st.session_state.logged_in:
        st.warning("🔒 이 서비스는 로그인한 사용자만 조회가 가능합니다. 먼저 로그인해 주세요.")
        st.info("사이드바 또는 상단 메뉴에서 로그인/회원가입 페이지로 이동해 주세요.")
    else:
        # User details status header
        is_admin = st.session_state.user_info.get('is_admin', False)
        role_label = "관리자" if is_admin else "일반 교육생"
        st.markdown(f"""
        <div class="user-status-banner">
            <div>
                <strong>👤 사용자:</strong> {st.session_state.user_info['name']} ({st.session_state.user_info['username']}) | 
                <strong>권한:</strong> {role_label}
            </div>
            <div>
                📍 학습 및 편집 모듈
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Load Curriculum
        curr_list = database.load_curriculum()
        
        if not curr_list:
            st.warning("등록된 커리큘럼 단원이 없습니다. 관리자 권한으로 단원을 추가하세요.")
            # If admin, show add button anyway
            if is_admin:
                new_title = st.text_input("새 첫 단원 제목", placeholder="예: 1회차 바이브 코딩 맛보기")
                if st.button("➕ 첫 단원 추가"):
                    if new_title:
                        new_chapter = {
                            "id": "1",
                            "title": new_title,
                            "content": f"# {new_title}\n\n새 단원이 추가되었습니다. 마크다운 내용을 채워보세요!"
                        }
                        database.save_curriculum([new_chapter])
                        st.success("단원이 추가되었습니다!")
                        st.rerun()
                    else:
                        st.error("단원 제목을 입력해주세요.")
        else:
            # Sort curriculum by numeric ID where possible
            def parse_id(item):
                try:
                    return float(item['id'])
                except ValueError:
                    return 999.0
            
            curr_list = sorted(curr_list, key=parse_id)
            
            # Selectbox for Chapter Choice
            titles = [f"{c['id']}단원 - {c['title']}" for c in curr_list]
            
            # Find selected index in list
            try:
                selected_idx = [c['id'] for c in curr_list].index(st.session_state.selected_chapter_id)
            except ValueError:
                selected_idx = 0
                st.session_state.selected_chapter_id = curr_list[0]['id']
                
            col_select, col_empty = st.columns([1, 1])
            with col_select:
                selected_title_opt = st.selectbox(
                    "📖 학습하실 교육 단원을 선택하세요:",
                    titles,
                    index=selected_idx
                )
            
            # Get actual selected chapter dictionary
            selected_chapter = curr_list[titles.index(selected_title_opt)]
            st.session_state.selected_chapter_id = selected_chapter['id']
            
            # Admin Mode Toggle
            edit_enabled = False
            if is_admin:
                st.write("")
                edit_enabled = st.checkbox(
                    "🛠️ 콘텐츠 편집 모드 활성화",
                    value=st.session_state.edit_mode,
                    help="체크하면 단원 추가, 삭제, 슬라이드 콘텐츠 실시간 편집 폼이 활성화됩니다."
                )
                st.session_state.edit_mode = edit_enabled
                st.write("---")
                
            # If Admin Mode is active, render editing tools
            if edit_enabled and is_admin:
                st.subheader("🛠️ 관리자 콘텐츠 관리 시스템 (CMS)")
                
                # Layout for Section Actions: Add and Delete
                col_add, col_del = st.columns(2)
                
                with col_add:
                    st.markdown("<div style='background-color: #1e293b; padding: 1.2rem; border-radius: 8px; border: 1px solid #475569;'>", unsafe_allow_html=True)
                    st.write("➕ **새 교육 단원 추가**")
                    new_ch_title = st.text_input("새 단원 제목 입력", placeholder="예: 5회차 심화 과제", key="new_ch_title_input")
                    if st.button("새 단원 생성하기", use_container_width=True):
                        if not new_ch_title:
                            st.error("단원 제목을 입력해주세요.")
                        else:
                            # Generate unique ID
                            existing_ids = []
                            for c in curr_list:
                                try:
                                    existing_ids.append(int(c['id']))
                                except ValueError:
                                    pass
                            new_ch_id = str(max(existing_ids) + 1) if existing_ids else "1"
                            
                            new_chapter = {
                                "id": new_ch_id,
                                "title": new_ch_title,
                                "content": f"# {new_ch_title}\n\n새 단원이 추가되었습니다. 여기에 실시간 교육용 슬라이드 내용을 작성하세요.\n\n### 💻 가이드 코드 블록\n```python\n# 코드를 작성하세요\n```"
                            }
                            
                            curr_list.append(new_chapter)
                            database.save_curriculum(curr_list)
                            st.session_state.selected_chapter_id = new_ch_id
                            st.success(f"새 단원이 추가되었습니다! (ID: {new_ch_id})")
                            st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                with col_del:
                    st.markdown("<div style='background-color: #1e293b; padding: 1.2rem; border-radius: 8px; border: 1px solid #475569;'>", unsafe_allow_html=True)
                    st.write("🗑️ **현재 단원 삭제**")
                    st.write(f"현재 선택된 단원: `{selected_chapter['id']}단원 - {selected_chapter['title']}`")
                    st.write("⚠️ 단원 삭제 시 포함된 모든 슬라이드 및 내용이 완전히 유실됩니다.")
                    if st.button("⚠️ 현재 단원 완전히 삭제하기", type="primary", use_container_width=True):
                        # Filter out the selected chapter
                        updated_list = [c for c in curr_list if c['id'] != selected_chapter['id']]
                        database.save_curriculum(updated_list)
                        st.warning("단원이 성공적으로 삭제되었습니다.")
                        # Reset selected chapter to the first one available
                        if updated_list:
                            st.session_state.selected_chapter_id = updated_list[0]['id']
                        else:
                            st.session_state.selected_chapter_id = "1"
                        st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)
                
                st.write("")
                st.markdown("📝 **현재 단원 및 슬라이드 실시간 수정**")
                
                edited_title = st.text_input(
                    "단원 제목 수정",
                    value=selected_chapter['title'],
                    key="title_editor_input",
                    help="단원의 제목을 수정합니다."
                )
                
                # Checkbox to toggle student visibility of PPT slides
                slides_visible_tgl = st.checkbox(
                    "🖥️ PPT 슬라이드를 일반 교육생에게 노출",
                    value=selected_chapter.get('slides_visible', True),
                    key=f"slides_visible_tgl_{selected_chapter['id']}",
                    help="체크를 해제하면 일반 교육생은 해당 단원의 PPT 슬라이드를 볼 수 없으며 과정 소개 및 가이드 문서만 열람 가능합니다."
                )
                
                edited_content = st.text_area(
                    "과정 소개 및 실습 가이드 편집기 (마크다운 지원)",
                    value=selected_chapter['content'],
                    height=350,
                    key="content_editor_area",
                    help="단원 소개 및 교육 가이드 내용을 마크다운으로 입력해 주세요."
                )
                
                if st.button("💾 과정 소개 및 단원명 저장하기", type="primary", use_container_width=True):
                    if not edited_title.strip():
                        st.error("단원 제목을 입력해 주세요.")
                    else:
                        # Update title, content, and visibility in original curriculum list
                        for idx, c in enumerate(curr_list):
                            if c['id'] == selected_chapter['id']:
                                curr_list[idx]['title'] = edited_title.strip()
                                curr_list[idx]['content'] = edited_content
                                curr_list[idx]['slides_visible'] = slides_visible_tgl
                                break
                        database.save_curriculum(curr_list)
                        st.success("💾 단원명, 노출 제어 및 과정 소개글 수정 사항이 성공적으로 저장되었습니다!")
                        st.rerun()
                        
                st.write("")
                st.markdown("🖥️ **현재 단원 PPTX/PDF 슬라이드 파일 관리**")
                uploaded_file = st.file_uploader(
                    "슬라이드 파일 업로드 (.pptx 또는 .pdf)",
                    type=["pptx", "pdf"],
                    key=f"slide_uploader_{selected_chapter['id']}"
                )
                
                if uploaded_file is not None:
                    # Save target PDF path
                    pdf_filename = f"slides_{selected_chapter['id']}.pdf"
                    pdf_path = os.path.join(database.SLIDES_DIR, pdf_filename)
                    
                    # Read bytes
                    file_bytes = uploaded_file.read()
                    
                    if uploaded_file.name.endswith(".pdf"):
                        with open(pdf_path, "wb") as f:
                            f.write(file_bytes)
                        # Delete corresponding notes file if it exists to avoid stale notes
                        notes_path = os.path.join(database.SLIDES_DIR, f"notes_{selected_chapter['id']}.json")
                        if os.path.exists(notes_path):
                            try:
                                os.remove(notes_path)
                            except Exception:
                                pass
                        st.success(f"🎉 PDF 슬라이드 파일이 성공적으로 저장되었습니다! ({uploaded_file.name})")
                        st.rerun()
                    elif uploaded_file.name.endswith(".pptx"):
                        # Save temporary pptx
                        temp_pptx_path = os.path.join(database.SLIDES_DIR, f"temp_{selected_chapter['id']}.pptx")
                        with open(temp_pptx_path, "wb") as f:
                            f.write(file_bytes)
                        
                        # Call win32com PPTX-to-PDF conversion helper
                        with st.spinner("PowerPoint 파일을 PDF로 변환하는 중..."):
                            success = database.convert_pptx_to_pdf(temp_pptx_path, pdf_path)
                            
                        # Extract slide notes from PPTX
                        if success:
                            notes_path = os.path.join(database.SLIDES_DIR, f"notes_{selected_chapter['id']}.json")
                            database.extract_pptx_notes(temp_pptx_path, notes_path)
                            
                        # Cleanup temp pptx
                        if os.path.exists(temp_pptx_path):
                            try:
                                os.remove(temp_pptx_path)
                            except Exception:
                                pass
                            except Exception:
                                pass
                                
                        if success:
                            st.success(f"🎉 PowerPoint 파일이 성공적으로 업로드 및 변환되어 저장되었습니다! ({uploaded_file.name})")
                            st.rerun()
                        else:
                            st.error("❌ PowerPoint 파일 변환에 실패했습니다. 로컬 컴퓨터에 Microsoft PowerPoint가 설치되어 있는지 확인해 주세요. 혹은 직접 PDF로 변환 후 업로드해 주시기 바랍니다.")
                
                st.write("---")
            
            # Content Presentation (Trainee and Admin View)
            st.subheader("📄 교육 콘텐츠 학습 센터")
            
            tab_guide, tab_slides = st.tabs(["📖 과정 소개 및 실습 가이드", "🖥️ PPT 슬라이드 프리젠테이션"])
            
            with tab_guide:
                # Wide Layout Styling for slide panel
                st.markdown(f"""
                <div style="background-color: #1e293b; padding: 2.5rem; border-radius: 12px; border: 1px solid #334155; margin-bottom: 2rem;">
                    <div style="font-size: 0.95rem; font-weight: bold; color: #818cf8; margin-bottom: 1rem; border-bottom: 1px solid #475569; padding-bottom: 0.5rem; text-transform: uppercase;">
                        {selected_chapter['id']}단원 - {selected_chapter['title']} (과정 소개)
                    </div>
                    <div>
                """, unsafe_allow_html=True)
                
                st.markdown(selected_chapter['content'])
                
                st.markdown("""
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
            with tab_slides:
                is_slide_visible = selected_chapter.get('slides_visible', True)
                
                # Check if slide is visible or user is admin
                if not is_slide_visible and not is_admin:
                    st.markdown("""
                    <div style="
                        background-color: #1e293b; 
                        border-left: 4px solid #f59e0b; 
                        border-radius: 12px; 
                        padding: 3rem; 
                        text-align: center; 
                        border-top: 1px solid #334155; 
                        border-right: 1px solid #334155; 
                        border-bottom: 1px solid #334155;
                        box-shadow: 0 10px 25px rgba(245, 158, 11, 0.1);
                        margin-bottom: 2rem;
                    ">
                        <div style="font-size: 3.5rem; margin-bottom: 1.25rem; filter: drop-shadow(0 0 10px rgba(245, 158, 11, 0.2));">🔒</div>
                        <h3 style="color: #f59e0b; font-weight: 700; margin-bottom: 0.75rem;">현재 비공개 상태인 슬라이드입니다</h3>
                        <p style="color: #94a3b8; font-size: 1rem; line-height: 1.7; margin: 0 auto; max-width: 600px;">
                            본 단원의 PPT 슬라이드 프레젠테이션은 교육 과정 진행 상황에 따라 순차적으로 공개될 예정입니다.<br>
                            왼쪽의 <b>'📖 과정 소개 및 실습 가이드'</b> 탭에서 제공되는 강의 소개 및 코드 실습 가이드를 활용해 학습해 주세요!
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    pdf_path = os.path.join(database.SLIDES_DIR, f"slides_{selected_chapter['id']}.pdf")
                    
                    if os.path.exists(pdf_path):
                        # Cache rendering to avoid re-rendering pages on every slide change
                        @st.cache_data(show_spinner="슬라이드 로딩 중...")
                        def get_cached_slides(path, mtime):
                            return render_pdf_to_images(path)
                            
                        mtime = os.path.getmtime(pdf_path)
                        slide_images = get_cached_slides(pdf_path, mtime)
                        
                        if slide_images:
                            slide_state_key = f"pdf_slide_idx_{selected_chapter['id']}"
                            if slide_state_key not in st.session_state:
                                st.session_state[slide_state_key] = 0
                                
                            current_idx = st.session_state[slide_state_key]
                            if current_idx >= len(slide_images):
                                current_idx = 0
                                st.session_state[slide_state_key] = 0
                                
                            # Draw PPT Card container
                            st.markdown(f"""
                            <div style="
                                background-color: #111827; 
                                border: 2px solid #6366f1; 
                                border-radius: 16px; 
                                padding: 1.5rem; 
                                text-align: center; 
                                box-shadow: 0 10px 25px rgba(99, 102, 241, 0.2); 
                                position: relative; 
                                margin-bottom: 1.5rem;
                            ">
                                <div style="position: absolute; top: 0.75rem; right: 1rem; font-size: 0.8rem; color: #818cf8; font-weight: bold; border: 1px solid #4f46e5; padding: 0.2rem 0.5rem; border-radius: 4px; background: rgba(99, 102, 241, 0.15); z-index: 10;">
                                    SLIDE {current_idx + 1} / {len(slide_images)}
                                </div>
                            """, unsafe_allow_html=True)
                            
                            st.image(slide_images[current_idx], use_column_width=True)
                            
                            st.markdown("</div>", unsafe_allow_html=True)
                            
                            # Slide controls
                            col_prev, col_num, col_next = st.columns([1, 2, 1])
                            with col_prev:
                                if st.button("◀ 이전 슬라이드", use_container_width=True, disabled=(current_idx == 0), key=f"pdf_prev_{selected_chapter['id']}"):
                                    st.session_state[slide_state_key] -= 1
                                    st.rerun()
                            with col_num:
                                st.markdown(f"<div style='text-align: center; font-weight: bold; color: #94a3b8; font-size: 1.1rem; padding-top: 0.4rem;'>슬라이드 {current_idx + 1} / {len(slide_images)}</div>", unsafe_allow_html=True)
                            with col_next:
                                if st.button("다음 슬라이드 ▶", use_container_width=True, disabled=(current_idx == len(slide_images) - 1), key=f"pdf_next_{selected_chapter['id']}"):
                                    st.session_state[slide_state_key] += 1
                                    st.rerun()
                                    
                            # Fetch and display slide notes
                            notes_path = os.path.join(database.SLIDES_DIR, f"notes_{selected_chapter['id']}.json")
                            slide_notes = []
                            if os.path.exists(notes_path):
                                try:
                                    import json
                                    with open(notes_path, "r", encoding="utf-8") as f:
                                        slide_notes = json.load(f)
                                except Exception:
                                    pass
                                    
                            st.write("")
                            if slide_notes and current_idx < len(slide_notes) and slide_notes[current_idx].strip():
                                st.markdown(f"""
                                <div style="
                                    background-color: #1e293b; 
                                    border-left: 4px solid #6366f1; 
                                    border-radius: 8px; 
                                    padding: 1.25rem; 
                                    border-top: 1px solid #334155; 
                                    border-right: 1px solid #334155; 
                                    border-bottom: 1px solid #334155;
                                ">
                                    <div style="font-weight: 700; color: #818cf8; font-size: 0.95rem; margin-bottom: 0.5rem; display: flex; align-items: center; gap: 0.5rem;">
                                        📝 자율학습 가이드 (강사 슬라이드 노트)
                                    </div>
                                    <div style="color: #cbd5e1; font-size: 0.95rem; line-height: 1.6; white-space: pre-wrap;">{slide_notes[current_idx]}</div>
                                </div>
                                """, unsafe_allow_html=True)
                            else:
                                st.markdown(f"""
                                <div style="
                                    background-color: #1e293b; 
                                    border-left: 4px solid #475569; 
                                    border-radius: 8px; 
                                    padding: 1rem; 
                                    border-top: 1px solid #334155; 
                                    border-right: 1px solid #334155; 
                                    border-bottom: 1px solid #334155; 
                                    font-style: italic; 
                                    color: #94a3b8; 
                                    font-size: 0.9rem;
                                ">
                                    💡 이 슬라이드에는 등록된 강사 노트가 없습니다. 자율학습 가이드를 보시려면 PPTX 업로드 시 슬라이드 노트를 채워주세요.
                                </div>
                                """, unsafe_allow_html=True)
                        else:
                            st.warning("⚠️ 슬라이드 파일을 로드할 수 없거나 비어 있습니다.")
                    else:
                        st.info("💡 등록된 PPT/PDF 슬라이드 파일이 없습니다. 관리자인 경우 콘텐츠 편집 모드에서 슬라이드 파일을 업로드해 주세요.")



# --- PAGE 3: Q&A 모듈 ---
elif menu == "💬 실시간 1:1 질의응답 (Q&A)":
    # Login Guard
    if not st.session_state.logged_in:
        st.warning("🔒 Q&A 서비스는 로그인 후에 사용할 수 있습니다. 먼저 로그인해 주세요.")
        st.info("사이드바 메뉴에서 로그인/회원가입 페이지로 이동해 주세요.")
    else:
        is_admin = st.session_state.user_info.get('is_admin', False)
        role_label = "관리자" if is_admin else "교육생"
        current_user = st.session_state.user_info

        st.markdown(f"""
        <div class="user-status-banner">
            <div>
                <strong>👤 사용자:</strong> {current_user['name']} ({current_user['username']}) |
                <strong>권한:</strong> {role_label}
            </div>
            <div>💬 실시간 질의응답 레코드</div>
        </div>
        """, unsafe_allow_html=True)

        # ── New question form (all logged-in users) ───────────────────────────
        st.subheader("❓ 새로운 질문 등록하기")
        with st.form("qna_submit_form", clear_on_submit=True):
            question_text = st.text_area(
                "궁금한 내용을 상세히 적어주세요. 누구든 답변을 남길 수 있습니다.",
                placeholder="예: 3회차 Streamlit 코드 실행 시 포트 8501이 이미 사용 중이라는 오류가 납니다. 어떻게 해결하나요?",
                height=130
            )
            submitted = st.form_submit_button("💬 질문 제출하기", type="primary")
            if submitted:
                if not question_text.strip():
                    st.error("질문 내용을 작성해주세요.")
                else:
                    qna_list = database.load_qna()
                    used_ids = {int(q['id']) for q in qna_list if q['id'].isdigit()}
                    new_id = str(max(used_ids, default=0) + 1)
                    qna_list.append({
                        "id": new_id,
                        "username": current_user['username'],
                        "name": current_user['name'],
                        "question": question_text.strip(),
                        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "answers": []
                    })
                    database.save_qna(qna_list)
                    st.success("🎉 질문이 정상적으로 제출되었습니다!")
                    st.rerun()

        st.write("")
        st.subheader("📋 전체 질의응답 목록")
        qna_list = database.load_qna()

        if not qna_list:
            st.info("등록된 질의응답이 없습니다. 첫 질문을 남겨보세요!")
        else:
            for qna in reversed(qna_list):
                answers = qna.get("answers", [])
                badge_color = "#10b981" if answers else "#f59e0b"
                badge_text = f"✅ 답변 {len(answers)}개" if answers else "⏳ 답변 대기"

                st.markdown(f"""
                <div class="qna-card">
                    <div class="question-header">
                        <div class="question-author">👤 {qna['name']} ({qna['username']})</div>
                        <div style="display:flex; gap:0.5rem; align-items:center;">
                            <span style="background:{badge_color}22; color:{badge_color}; font-size:0.8rem; font-weight:700; padding:0.15rem 0.6rem; border-radius:999px; border:1px solid {badge_color}44;">{badge_text}</span>
                            <span class="question-date">📅 {qna['created_at']}</span>
                        </div>
                    </div>
                    <div class="question-body">{qna['question']}</div>
                """, unsafe_allow_html=True)

                # Show existing answers
                for ans in answers:
                    is_admin_ans = "(관리자)" if ans.get('username') == 'admin' else ""
                    st.markdown(f"""
                    <div class="answer-section">
                        <div class="answer-header">
                            💬 {ans['name']} ({ans['username']}) {is_admin_ans} &nbsp;·&nbsp; {ans.get('answered_at', '')}
                        </div>
                        <div class="answer-body">{ans['answer']}</div>
                    </div>
                    """, unsafe_allow_html=True)

                if not answers:
                    st.markdown('<span class="answer-pending">⏳ 아직 답변이 없습니다. 먼저 답변을 달아보세요!</span>', unsafe_allow_html=True)

                st.markdown("</div>", unsafe_allow_html=True)

                # Answer form (all logged-in users)
                with st.expander(f"✏️ 답변 달기 (질문 #{qna['id']})", expanded=False):
                    new_ans_text = st.text_area(
                        "답변 내용",
                        placeholder="도움이 되는 답변을 남겨주세요.",
                        key=f"ans_input_{qna['id']}",
                        height=90
                    )
                    if st.button("💾 답변 등록하기", key=f"ans_btn_{qna['id']}", type="primary"):
                        if not new_ans_text.strip():
                            st.error("답변 내용을 입력해주세요.")
                        else:
                            fresh = database.load_qna()
                            for idx, item in enumerate(fresh):
                                if item['id'] == qna['id']:
                                    existing = fresh[idx].get("answers", [])
                                    ans_ids = {int(a['id']) for a in existing if str(a.get('id', '')).isdigit()}
                                    new_ans_id = str(max(ans_ids, default=0) + 1)
                                    fresh[idx]["answers"] = existing + [{
                                        "id": new_ans_id,
                                        "username": current_user['username'],
                                        "name": current_user['name'],
                                        "answer": new_ans_text.strip(),
                                        "answered_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                    }]
                                    break
                            database.save_qna(fresh)
                            st.success("답변이 등록되었습니다!")
                            st.rerun()

                # Admin: delete question
                if is_admin:
                    if st.button(f"🗑️ 이 질문 삭제", key=f"del_q_{qna['id']}", type="secondary"):
                        fresh = database.load_qna()
                        fresh = [q for q in fresh if q['id'] != qna['id']]
                        database.save_qna(fresh)
                        st.warning(f"질문 #{qna['id']}이 삭제되었습니다.")
                        st.rerun()


# --- PAGE 4: 관리자 전용 - 회원 & Q&A 관리 ---
elif menu == "👥 회원 및 Q&A 관리 (Admin)":
    if not (st.session_state.logged_in and st.session_state.user_info.get('is_admin')):
        st.error("🚫 관리자만 접근할 수 있는 페이지입니다.")
    else:
        st.markdown("""
        <div class="user-status-banner">
            <div><strong>🔧 관리자 전용 패널</strong></div>
            <div>👥 회원 및 Q&A 데이터 관리</div>
        </div>
        """, unsafe_allow_html=True)

        admin_tab1, admin_tab2 = st.tabs(["👥 회원 목록 관리", "💬 Q&A 전체 관리"])

        # ── Member Management ─────────────────────────────────────────────────
        with admin_tab1:
            st.subheader("👥 등록된 회원 목록")
            users = database.load_users()
            if not users:
                st.info("등록된 회원이 없습니다.")
            else:
                for uname, udata in list(users.items()):
                    role_txt = "🔑 관리자" if udata.get('is_admin') else "🎓 교육생"
                    col_info, col_del = st.columns([5, 1])
                    with col_info:
                        st.markdown(f"""
                        <div style="background:#0f172a; border:1px solid #334155; border-radius:8px; padding:0.75rem 1rem; margin-bottom:0.5rem; display:flex; align-items:center; gap:1.5rem;">
                            <div style="font-weight:700; color:#f1f5f9; font-size:1rem;">{udata.get('name', uname)}</div>
                            <div style="color:#64748b; font-size:0.88rem;">@{uname}</div>
                            <span style="background:{'#d97706' if udata.get('is_admin') else '#2563eb'}22; color:{'#f59e0b' if udata.get('is_admin') else '#60a5fa'}; font-size:0.78rem; font-weight:700; padding:0.1rem 0.55rem; border-radius:999px;">{role_txt}</span>
                        </div>
                        """, unsafe_allow_html=True)
                    with col_del:
                        # Prevent self-deletion
                        if uname == st.session_state.user_info['username']:
                            st.markdown("<div style='padding:0.85rem 0; color:#475569; font-size:0.8rem;'>본인 계정</div>", unsafe_allow_html=True)
                        else:
                            if st.button("🗑️", key=f"del_user_{uname}", help=f"{uname} 삭제"):
                                users.pop(uname)
                                database.save_users(users)
                                st.success(f"회원 '{uname}'이 삭제되었습니다.")
                                st.rerun()

        # ── Q&A Management ────────────────────────────────────────────────────
        with admin_tab2:
            st.subheader("💬 전체 Q&A 레코드 관리")
            qna_list = database.load_qna()
            if not qna_list:
                st.info("등록된 Q&A 레코드가 없습니다.")
            else:
                # Bulk delete
                if st.button("🗑️ 전체 Q&A 레코드 초기화", type="secondary", use_container_width=True):
                    database.save_qna([])
                    st.success("전체 Q&A 레코드가 초기화되었습니다.")
                    st.rerun()

                st.write("")
                for qna in reversed(qna_list):
                    answers = qna.get("answers", [])
                    col_q, col_del = st.columns([6, 1])
                    with col_q:
                        st.markdown(f"""
                        <div style="background:#1e293b; border:1px solid #334155; border-radius:8px; padding:0.75rem 1rem; margin-bottom:0.4rem;">
                            <div style="display:flex; justify-content:space-between; margin-bottom:0.4rem;">
                                <span style="font-weight:600; color:#f1f5f9;">Q#{qna['id']} — {qna['name']} ({qna['username']})</span>
                                <span style="font-size:0.8rem; color:#64748b;">{qna['created_at']}</span>
                            </div>
                            <div style="color:#cbd5e1; font-size:0.9rem; white-space:pre-wrap; margin-bottom:0.35rem;">{qna['question'][:200]}{'...' if len(qna['question']) > 200 else ''}</div>
                            <span style="font-size:0.78rem; color:#94a3b8;">💬 답변 {len(answers)}개</span>
                        </div>
                        """, unsafe_allow_html=True)
                    with col_del:
                        if st.button("🗑️", key=f"admin_del_q_{qna['id']}", help=f"Q#{qna['id']} 삭제"):
                            fresh = database.load_qna()
                            fresh = [q for q in fresh if q['id'] != qna['id']]
                            database.save_qna(fresh)
                            st.success(f"Q#{qna['id']}이 삭제되었습니다.")
                            st.rerun()
