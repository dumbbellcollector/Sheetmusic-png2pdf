import streamlit as st
import os
import re
from PIL import Image
import io  # 메모리 처리를 위한 라이브러리
import base64 # PDF 미리보기를 위한 라이브러리

# --- PDF 생성 로직 (기능 추가) ---

def natural_sort_key(s):
    """자연어 정렬(Natural Sort)을 위한 키 함수. Streamlit의 UploadedFile 객체를 처리하도록 수정."""
    return [int(text) if text.isdigit() else text.lower() for text in re.split(r'([0-9]+)', s.name)]

def create_a4_pdf_from_images(image_files, output_dpi, spacing_mm, fix_height):
    """
    업로드된 이미지 파일들을 받아 메모리 상에서 PDF를 생성하고 바이트 데이터로 반환합니다.
    '세로 크기 고정' 옵션을 추가했습니다.
    """
    A4_WIDTH_IN, A4_HEIGHT_IN = 8.27, 11.69
    canvas_width_px = int(A4_WIDTH_IN * output_dpi)
    canvas_height_px = int(A4_HEIGHT_IN * output_dpi)
    spacing_px = int((spacing_mm / 25.4) * output_dpi)
    
    sorted_image_files = sorted(image_files, key=natural_sort_key)

    safe_ref_height_in = None
    # '세로 크기 고정' 옵션이 켜져 있고, 이미지가 2개 이상일 때 기준 높이 계산
    if fix_height and len(sorted_image_files) > 1:
        try:
            # 1. 두 번째 이미지로부터 기준 높이를 가져옴
            ref_img_file = sorted_image_files[1]
            ref_img_file.seek(0)
            ref_img = Image.open(ref_img_file).convert('RGB')
            ref_dpi_info = ref_img.info.get('dpi')
            ref_source_dpi = ref_dpi_info[0] if ref_dpi_info else 72
            ref_physical_height_in = ref_img.height / ref_source_dpi

            # 2. 모든 이미지 중 가장 넓은 가로/세로 비율을 찾음
            max_aspect_ratio = 0
            for file in sorted_image_files:
                file.seek(0)
                img_temp = Image.open(file).convert('RGB')
                if img_temp.height > 0:
                    aspect_ratio = img_temp.width / img_temp.height
                    if aspect_ratio > max_aspect_ratio:
                        max_aspect_ratio = aspect_ratio
            
            # 3. 기준 높이를 적용했을 때 가장 넓은 이미지가 페이지 너비를 초과하는지 확인
            potential_max_width_in = ref_physical_height_in * max_aspect_ratio
            if potential_max_width_in > A4_WIDTH_IN:
                # 4. 초과한다면, 페이지 너비에 맞게 기준 높이를 안전하게 재조정
                safe_ref_height_in = A4_WIDTH_IN / max_aspect_ratio
            else:
                # 5. 초과하지 않는다면, 원래 기준 높이를 그대로 사용
                safe_ref_height_in = ref_physical_height_in
        except Exception as e:
            st.error(f"세로 크기 고정 기능 처리 중 오류 발생: {e}")
            fix_height = False # 오류 발생 시 기능 비활성화

    pdf_pages = []
    current_page = Image.new('RGB', (canvas_width_px, canvas_height_px), 'white')
    y_offset = spacing_px
    
    total_images = len(sorted_image_files)
    progress_bar = st.progress(0, text="PDF 생성 중...")

    for idx, uploaded_file in enumerate(sorted_image_files):
        uploaded_file.seek(0) # 각 파일 처리 전 스트림 위치 초기화
        img = Image.open(uploaded_file).convert('RGB')
        
        dpi_info = img.info.get('dpi')
        source_dpi = dpi_info[0] if dpi_info else 72
        
        original_width_px, original_height_px = img.size
        img_physical_width_in = original_width_px / source_dpi
        img_physical_height_in = original_height_px / source_dpi

        # '세로 크기 고정' 로직 (수정됨)
        if fix_height and safe_ref_height_in is not None:
            # 모든 이미지의 높이를 안전하게 계산된 기준 높이로 설정
            target_physical_height_in = safe_ref_height_in
            # 비율에 맞춰 너비 계산
            aspect_ratio = img_physical_width_in / img_physical_height_in if img_physical_height_in > 0 else 0
            target_physical_width_in = target_physical_height_in * aspect_ratio
            x_offset = 0 # 왼쪽 정렬

        # 기본 로직 (페이지 너비에 맞춤)
        else:
            if img_physical_width_in > A4_WIDTH_IN:
                scale_ratio = A4_WIDTH_IN / img_physical_width_in
                target_physical_width_in = A4_WIDTH_IN
                target_physical_height_in = img_physical_height_in * scale_ratio
            else:
                target_physical_width_in = img_physical_width_in
                target_physical_height_in = img_physical_height_in
            x_offset = (canvas_width_px - int(target_physical_width_in * output_dpi)) // 2 # 중앙 정렬

        final_width_px = int(target_physical_width_in * output_dpi)
        final_height_px = int(target_physical_height_in * output_dpi)
        
        resized_img = img.resize((final_width_px, final_height_px), Image.Resampling.LANCZOS)
        
        if y_offset + final_height_px > canvas_height_px:
            pdf_pages.append(current_page)
            current_page = Image.new('RGB', (canvas_width_px, canvas_height_px), 'white')
            y_offset = spacing_px

        current_page.paste(resized_img, (x_offset, y_offset))
        y_offset += final_height_px + spacing_px

        progress_bar.progress((idx + 1) / total_images, text=f"이미지 처리 중: {idx + 1}/{total_images}")

    if y_offset > spacing_px:
        pdf_pages.append(current_page)

    pdf_buffer = io.BytesIO()
    if pdf_pages:
        pdf_pages[0].save(
            pdf_buffer, "PDF", resolution=output_dpi, save_all=True, append_images=pdf_pages[1:]
        )
        progress_bar.empty()
        return pdf_buffer.getvalue()
    else:
        progress_bar.empty()
        return None

# --- Streamlit UI 구성 ---

st.set_page_config(
    page_title="PNG to PDF Converter", page_icon="📄", layout="wide", initial_sidebar_state="expanded"
)

# --- 위젯 동기화를 위한 콜백 함수 ---
def sync_dpi_slider_from_num():
    st.session_state.dpi_slider = st.session_state.dpi_num

def sync_dpi_num_from_slider():
    st.session_state.dpi_num = st.session_state.dpi_slider

def sync_spacing_slider_from_num():
    st.session_state.spacing_slider = st.session_state.spacing_num

def sync_spacing_num_from_slider():
    st.session_state.spacing_num = st.session_state.spacing_slider

st.title("📄 PNG를 PDF로 변환하기")
st.markdown("여러 개의 PNG 파일을 A4 사이즈 PDF 문서 한 개로 만들어보세요.")

# --- 사이드바 설정 (연동 기능 수정) ---
st.sidebar.header("⚙️ PDF 설정")

# 세션 상태 초기화 (여백 기본값 0으로 수정)
if 'dpi_num' not in st.session_state:
    st.session_state.dpi_num = 300
if 'dpi_slider' not in st.session_state:
    st.session_state.dpi_slider = 300
if 'spacing_num' not in st.session_state:
    st.session_state.spacing_num = 0
if 'spacing_slider' not in st.session_state:
    st.session_state.spacing_slider = 0

fix_height_option = st.sidebar.checkbox(
    "세로 크기 고정 (두 번째 이미지 기준)", 
    value=False,
    help="가로가 좁은 이미지가 과도하게 확대되는 것을 방지합니다. 모든 이미지의 최대 세로 크기가 두 번째 이미지의 높이로 제한되며, 이미지는 왼쪽에 정렬됩니다. (2개 이상 파일 필요)"
)

# DPI 설정: 숫자 입력과 슬라이더 연동
st.sidebar.number_input(
    "출력 PDF 해상도 (DPI)", min_value=72, max_value=1200, step=10,
    key='dpi_num',
    on_change=sync_dpi_slider_from_num,
    help="PDF의 전체적인 품질을 결정합니다. 숫자를 직접 입력하거나 아래 슬라이더를 조절하세요."
)
st.sidebar.slider("DPI 슬라이더", 72, 1200,
    key='dpi_slider',
    on_change=sync_dpi_num_from_slider
)

# 여백 설정: 숫자 입력과 슬라이더 연동
st.sidebar.number_input(
    "이미지 사이 여백 (mm)", min_value=0, max_value=50, step=1,
    key='spacing_num',
    on_change=sync_spacing_slider_from_num,
    help="PDF 페이지 안에서 이미지와 이미지 사이의 세로 간격을 조절합니다."
)
st.sidebar.slider("여백 슬라이더 (mm)", 0, 50,
    key='spacing_slider',
    on_change=sync_spacing_num_from_slider
)

# --- 메인 화면 구성 ---
uploaded_files = st.file_uploader(
    "여기에 PNG 파일을 드래그 앤 드롭하거나 클릭하여 업로드하세요.",
    type=["png"], accept_multiple_files=True
)

if st.button("🚀 PDF 생성하기", type="primary", use_container_width=True):
    if uploaded_files:
        with st.spinner("PDF를 생성하고 있습니다. 잠시만 기다려주세요..."):
            # 세션 상태에서 최종 값을 가져와 사용
            output_dpi = st.session_state.dpi_num
            spacing_mm = st.session_state.spacing_num
            pdf_data = create_a4_pdf_from_images(uploaded_files, output_dpi, spacing_mm, fix_height_option)
        
        if pdf_data:
            st.success("🎉 PDF 생성이 완료되었습니다!")
            st.session_state.pdf_data = pdf_data
            st.session_state.pdf_name = "converted_document.pdf"
        else:
            st.error("PDF를 생성하지 못했습니다. 이미지를 확인해주세요.")
    else:
        st.warning("먼저 PNG 파일을 업로드해주세요.")

if uploaded_files:
    with st.expander(f"업로드된 이미지 미리보기 ({len(uploaded_files)}개)", expanded=False):
        cols = st.columns(3)
        for i, file in enumerate(uploaded_files):
            cols[i % 3].image(file, caption=file.name, use_column_width=True)

if "pdf_data" in st.session_state:
    st.download_button(
        label="⬇️ PDF 다운로드", data=st.session_state.pdf_data,
        file_name=st.session_state.pdf_name, mime="application/pdf", use_container_width=True
    )
    
    with st.container():
        st.subheader("📄 PDF 미리보기")
        base64_pdf = base64.b64encode(st.session_state.pdf_data).decode('utf-8')
        pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="1000" type="application/pdf"></iframe>'
        st.markdown(pdf_display, unsafe_allow_html=True)

# streamlit run app.py