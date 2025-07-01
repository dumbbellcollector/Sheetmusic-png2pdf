import streamlit as st
import os
import re
from PIL import Image
import io  # 메모리 처리를 위한 라이브러리

# --- PDF 생성 로직 (기존 코드를 함수로 정리) ---
# 이 함수는 이제 파일 경로 대신 메모리에 있는 파일 데이터를 직접 다룹니다.

def natural_sort_key(s):
    """자연어 정렬(Natural Sort)을 위한 키 함수."""
    return [int(text) if text.isdigit() else text.lower() for text in re.split(r'([0-9]+)', s.name)]

def create_a4_pdf_from_images(image_files, output_dpi, spacing_mm):
    """
    업로드된 이미지 파일들을 받아 메모리 상에서 PDF를 생성하고 바이트 데이터로 반환합니다.
    """
    A4_WIDTH_IN, A4_HEIGHT_IN = 8.27, 11.69
    canvas_width_px = int(A4_WIDTH_IN * output_dpi)
    canvas_height_px = int(A4_HEIGHT_IN * output_dpi)
    spacing_px = int((spacing_mm / 25.4) * output_dpi)
    
    # 파일 이름으로 정렬
    sorted_image_files = sorted(image_files, key=natural_sort_key)

    pdf_pages = []
    current_page = Image.new('RGB', (canvas_width_px, canvas_height_px), 'white')
    y_offset = spacing_px
    
    total_images = len(sorted_image_files)
    progress_bar = st.progress(0, text="PDF 생성 중...")

    for idx, uploaded_file in enumerate(sorted_image_files):
        img = Image.open(uploaded_file).convert('RGB')
        
        dpi_info = img.info.get('dpi')
        source_dpi = dpi_info[0] if dpi_info else 72
        
        original_width_px, original_height_px = img.size
        img_physical_width_in = original_width_px / source_dpi
        img_physical_height_in = original_height_px / source_dpi

        if img_physical_width_in > A4_WIDTH_IN:
            scale_ratio = A4_WIDTH_IN / img_physical_width_in
            target_physical_width_in = A4_WIDTH_IN
            target_physical_height_in = img_physical_height_in * scale_ratio
        else:
            target_physical_width_in = img_physical_width_in
            target_physical_height_in = img_physical_height_in

        final_width_px = int(target_physical_width_in * output_dpi)
        final_height_px = int(target_physical_height_in * output_dpi)
        
        resized_img = img.resize((final_width_px, final_height_px), Image.Resampling.LANCZOS)
        
        if y_offset + final_height_px > canvas_height_px:
            pdf_pages.append(current_page)
            current_page = Image.new('RGB', (canvas_width_px, canvas_height_px), 'white')
            y_offset = spacing_px

        x_offset = (canvas_width_px - final_width_px) // 2
        current_page.paste(resized_img, (x_offset, y_offset))
        y_offset += final_height_px + spacing_px

        # 진행 상황 업데이트
        progress_bar.progress((idx + 1) / total_images, text=f"이미지 처리 중: {idx + 1}/{total_images}")

    if y_offset > spacing_px:
        pdf_pages.append(current_page)

    # PDF를 메모리에 저장
    pdf_buffer = io.BytesIO()
    if pdf_pages:
        pdf_pages[0].save(
            pdf_buffer, 
            "PDF",
            resolution=output_dpi, 
            save_all=True, 
            append_images=pdf_pages[1:]
        )
        progress_bar.empty() # 진행 바 제거
        return pdf_buffer.getvalue()
    else:
        progress_bar.empty() # 진행 바 제거
        return None

# --- Streamlit UI 구성 ---

st.set_page_config(page_title="PNG to PDF Converter", page_icon="📄")

st.title("📄 PNG를 PDF로 변환하기")
st.markdown("여러 개의 PNG 파일을 A4 사이즈 PDF 문서 한 개로 만들어보세요.")

# 1. 파일 업로더
uploaded_files = st.file_uploader(
    "PNG 파일을 업로드하세요.",
    type=["png"],
    accept_multiple_files=True
)

# 2. PDF 설정
st.sidebar.header("⚙️ PDF 설정")
output_dpi = st.sidebar.slider(
    "출력 PDF 해상도 (DPI)", 
    min_value=72, 
    max_value=600, 
    value=300, 
    step=1,
    help="PDF의 전체적인 품질을 결정합니다. 높을수록 선명하지만 파일 크기가 커집니다."
)
spacing_mm = st.sidebar.slider(
    "이미지 사이 여백 (mm)", 
    min_value=0, 
    max_value=30, 
    value=5, 
    step=1,
    help="PDF 페이지 안에서 이미지와 이미지 사이의 세로 간격을 조절합니다."
)

# 3. PDF 생성 버튼
if st.button("🚀 PDF 생성하기", type="primary"):
    if uploaded_files:
        with st.spinner("PDF를 생성하고 있습니다. 잠시만 기다려주세요..."):
            pdf_data = create_a4_pdf_from_images(uploaded_files, output_dpi, spacing_mm)
        
        if pdf_data:
            st.success("🎉 PDF 생성이 완료되었습니다! 아래 버튼을 눌러 다운로드하세요.")
            # 생성된 PDF 데이터를 st.session_state에 저장하여 다운로드 버튼이 계속 접근할 수 있도록 함
            st.session_state.pdf_data = pdf_data
        else:
            st.error("PDF를 생성하지 못했습니다. 이미지를 확인해주세요.")
    else:
        st.warning("먼저 PNG 파일을 업로드해주세요.")

# 4. 다운로드 버튼 (PDF가 생성된 경우에만 보임)
if "pdf_data" in st.session_state:
    st.download_button(
        label="⬇️ PDF 다운로드",
        data=st.session_state.pdf_data,
        file_name="converted_document.pdf",
        mime="application/pdf"
    )