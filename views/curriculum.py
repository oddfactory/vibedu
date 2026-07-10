import streamlit as st
import database
import os
import fitz
import json

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

def render_curriculum_page():
    # Login Guard
    if not st.session_state.logged_in:
        st.warning("🔒 이 서비스는 로그인한 사용자만 조회가 가능합니다. 먼저 로그인해 주세요.")
        st.info("사이드바 또는 상단 메뉴에서 로그인/회원가입 페이지로 이동해 주세요.")
        return
        
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
        if is_admin:
            new_title = st.text_input("새 첫 단원 제목", placeholder="예: 1회차 바이브 코딩 맛보기")
            if st.button("➕ 첫 단원 추가"):
                if new_title:
                    database.add_chapter(new_title)
                    st.success("단원이 추가되었습니다!")
                    st.rerun()
                else:
                    st.error("단원 제목을 입력해주세요.")
        return

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
                    new_ch_id = database.add_chapter(new_ch_title)
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
                database.delete_chapter(selected_chapter['id'])
                st.warning("단원이 성공적으로 삭제되었습니다.")
                
                # Reset selected chapter to the first one available
                updated_list = database.load_curriculum()
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
                database.update_chapter(
                    selected_chapter['id'],
                    edited_title.strip(),
                    edited_content,
                    slides_visible_tgl
                )
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
            pdf_filename = f"slides_{selected_chapter['id']}.pdf"
            pdf_path = os.path.join(database.SLIDES_DIR, pdf_filename)
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
