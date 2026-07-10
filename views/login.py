import streamlit as st
import database
import json
from datetime import datetime, timedelta

def render_login_page(cookie_manager):
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
                success, msg = database.update_user_password(
                    st.session_state.user_info['username'],
                    current_pw,
                    new_pw
                )
                if not success:
                    st.error(msg)
                elif new_pw != new_pw_confirm:
                    st.error("새 비밀번호가 서로 일치하지 않습니다.")
                else:
                    st.success("🔒 비밀번호가 성공적으로 변경되었습니다! 다음 로그인 시 변경된 비밀번호를 사용하세요.")
        
        st.write("")
        if st.button("로그아웃 하기", type="primary", use_container_width=True):
            logout_user(cookie_manager)
            
    else:
        tab_login, tab_register = st.tabs(["🔑 로그인", "📝 회원가입"])
        
        # Login Tab
        with tab_login:
            st.write("등록된 계정 정보를 입력하세요.")
            login_id = st.text_input("아이디", key="login_id_input")
            login_pw = st.text_input("비밀번호", type="password", key="login_pw_input")
            
            if st.button("로그인", key="login_submit_btn", type="primary"):
                user_info = database.authenticate_user(login_id, login_pw)
                if user_info:
                    st.session_state.logged_in = True
                    st.session_state.user_info = user_info
                    st.session_state._force_logged_out = False  # Allow cookie restore next time
                    # Persist session in cookie (7-day expiry)
                    try:
                        cookie_manager.set(
                            "vibe_session",
                            json.dumps({"username": login_id}),
                            expires_at=datetime.now() + timedelta(days=7)
                        )
                    except Exception:
                        pass
                    st.success(f"환영합니다! {user_info['name']}님 로그인 성공.")
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
                if reg_pw != reg_pw_confirm:
                    st.error("비밀번호가 서로 일치하지 않습니다.")
                else:
                    success, msg = database.create_user(reg_id, reg_name, reg_pw)
                    if success:
                        st.success(msg + " 로그인 탭에서 로그인해 주세요.")
                    else:
                        st.error(msg)

def logout_user(cookie_manager):
    """Log out the current user session and refresh."""
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
