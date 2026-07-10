import streamlit as st
import database

def render_admin_page():
    if not (st.session_state.logged_in and st.session_state.user_info.get('is_admin')):
        st.error("🚫 관리자만 접근할 수 있는 페이지입니다.")
        return
        
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
                            database.delete_user(uname)
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
                database.clear_all_qna()
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
                        database.delete_question(qna['id'])
                        st.success(f"Q#{qna['id']}이 삭제되었습니다.")
                        st.rerun()
