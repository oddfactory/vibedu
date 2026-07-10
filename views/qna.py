import streamlit as st
import database
from datetime import datetime

def render_qna_page():
    # Login Guard
    if not st.session_state.logged_in:
        st.warning("🔒 Q&A 서비스는 로그인 후에 사용할 수 있습니다. 먼저 로그인해 주세요.")
        st.info("사이드바 메뉴에서 로그인/회원가입 페이지로 이동해 주세요.")
        return
        
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
                database.add_question(
                    current_user['username'],
                    current_user['name'],
                    question_text
                )
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
                        database.add_answer(
                            qna['id'],
                            current_user['username'],
                            current_user['name'],
                            new_ans_text
                        )
                        st.success("답변이 등록되었습니다!")
                        st.rerun()

            # Admin: delete question
            if is_admin:
                if st.button(f"🗑️ 이 질문 삭제", key=f"del_q_{qna['id']}", type="secondary"):
                    database.delete_question(qna['id'])
                    st.warning(f"질문 #{qna['id']}이 삭제되었습니다.")
                    st.rerun()
