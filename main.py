import streamlit as st
import database
import os
import json
import extra_streamlit_components as stx
from datetime import datetime, timedelta

import views.login
import views.curriculum
import views.qna
import views.admin

# Set page configurations
st.set_page_config(
    page_title="Vibe Coding All-in-One Platform",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom premium styling using CSS file
CSS_PATH = os.path.join(os.path.dirname(__file__), "style.css")
if os.path.exists(CSS_PATH):
    with open(CSS_PATH, "r", encoding="utf-8") as f:
        css_style = f.read()
    st.markdown(f"<style>{css_style}</style>", unsafe_allow_html=True)

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
        views.login.logout_user(cookie_manager)

# Header Section
st.markdown("""
<div class="title-container">
    <h1 class="main-title">비개발자용 바이브 코딩 올인원 교육 플랫폼</h1>
    <p class="sub-title">AI 협업 코딩 학습 및 콘텐츠 실시간 관리 포탈</p>
</div>
""", unsafe_allow_html=True)

# ── Page Routing ──────────────────────────────────────────────────────────────
if menu == "🔓 로그인 / 회원가입":
    views.login.render_login_page(cookie_manager)
elif menu == "📖 커리큘럼 마스터 (학습 및 편집)":
    views.curriculum.render_curriculum_page()
elif menu == "💬 실시간 1:1 질의응답 (Q&A)":
    views.qna.render_qna_page()
elif menu == "👥 회원 및 Q&A 관리 (Admin)":
    views.admin.render_admin_page()
