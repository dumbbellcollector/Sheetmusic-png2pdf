import os
import glob
import re
from PIL import Image

# --- 설정 (이 부분을 필요에 맞게 수정하세요) ---

# 1. PNG 이미지들이 있는 폴더 경로
INPUT_DIR = '/Users/yeojoon/Desktop/Screenshots' 

# 2. 생성될 PDF 파일의 이름과 경로
OUTPUT_PDF = 'result_auto_dpi.pdf'

# 3. 최종 PDF의 출력 해상도 (품질 결정)
OUTPUT_DPI = 400

# 4. 이미지와 이미지 사이의 수직 여백 (밀리미터 단위, mm)
SPACING_MM = 0

# --- 코드 시작 ---

def natural_sort_key(s):
    """자연어 정렬(Natural Sort)을 위한 키 함수."""
    return [int(text) if text.isdigit() else text.lower() for text in re.split(r'([0-9]+)', s)]

def create_a4_pdf_from_images(input_dir, output_pdf_path, output_dpi, spacing_mm):
    """
    각 이미지의 DPI를 자동으로 감지하여 최적의 고품질 PDF를 생성합니다.
    """
    A4_WIDTH_IN, A4_HEIGHT_IN = 8.27, 11.69

    # 최종 PDF 캔버스를 고해상도로 설정
    canvas_width_px = int(A4_WIDTH_IN * output_dpi)
    canvas_height_px = int(A4_HEIGHT_IN * output_dpi)
    
    # 여백을 고해상도 캔버스에 맞게 픽셀로 변환
    spacing_px = int((spacing_mm / 25.4) * output_dpi)
    
    search_path = os.path.join(input_dir, '*.png')
    image_paths = sorted(glob.glob(search_path), key=natural_sort_key)

    if not image_paths:
        print(f"'{input_dir}' 폴더에 PNG 파일이 없습니다. 작업을 종료합니다.")
        return

    print(f"총 {len(image_paths)}개의 PNG 파일을 찾았습니다.")
    print(f"PDF 생성 설정: 출력 품질 {output_dpi} DPI, 이미지별 DPI 자동 감지")

    pdf_pages = []
    
    current_page = Image.new('RGB', (canvas_width_px, canvas_height_px), 'white')
    y_offset = spacing_px
    
    for idx, path in enumerate(image_paths):
        img = Image.open(path).convert('RGB')
        original_width_px, original_height_px = img.size
        
        # --- (핵심 기능) 이미지의 DPI를 자동으로 읽어오기 ---
        # 이미지 정보에서 DPI를 읽어옴. 정보가 없으면 기본값 72를 사용.
        dpi_info = img.info.get('dpi')
        if dpi_info:
            source_dpi = dpi_info[0]
        else:
            source_dpi = 72  # DPI 정보가 없을 경우의 표준 기본값
        
        # 원본 이미지의 실제 물리적 크기(인치) 계산
        img_physical_width_in = original_width_px / source_dpi
        img_physical_height_in = original_height_px / source_dpi

        # 이미지가 A4 페이지보다 넓으면, A4 너비에 맞게 물리적 크기를 조정
        if img_physical_width_in > A4_WIDTH_IN:
            scale_ratio = A4_WIDTH_IN / img_physical_width_in
            target_physical_width_in = A4_WIDTH_IN
            target_physical_height_in = img_physical_height_in * scale_ratio
        else:
            target_physical_width_in = img_physical_width_in
            target_physical_height_in = img_physical_height_in

        # 조정된 물리적 크기를 고해상도 캔버스에 맞는 픽셀 크기로 다시 변환
        final_width_px = int(target_physical_width_in * output_dpi)
        final_height_px = int(target_physical_height_in * output_dpi)
        
        # 최종 픽셀 크기로 이미지 리사이즈
        resized_img = img.resize((final_width_px, final_height_px), Image.Resampling.LANCZOS)
        
        # 페이지 공간 확인 및 새 페이지 생성
        if y_offset + final_height_px > canvas_height_px:
            pdf_pages.append(current_page)
            print(f"{len(pdf_pages)}번째 페이지 생성 완료...")
            current_page = Image.new('RGB', (canvas_width_px, canvas_height_px), 'white')
            y_offset = spacing_px

        # 가로 중앙 정렬
        x_offset = (canvas_width_px - final_width_px) // 2
        
        current_page.paste(resized_img, (x_offset, y_offset))
        y_offset += final_height_px + spacing_px
    
    if y_offset > spacing_px:
        pdf_pages.append(current_page)
        print(f"{len(pdf_pages)}번째 페이지 생성 완료...")

    if pdf_pages:
        pdf_pages[0].save(
            output_pdf_path, 
            "PDF",
            resolution=output_dpi, 
            save_all=True, 
            append_images=pdf_pages[1:]
        )
        print(f"\n성공! '{output_pdf_path}' 파일이 생성되었습니다.")
    else:
        print("PDF로 만들 페이지가 없습니다.")

if __name__ == "__main__":
    # create_a4_pdf_from_images 함수 호출 시 SOURCE_IMAGE_DPI 인자 제거됨
    create_a4_pdf_from_images(INPUT_DIR, OUTPUT_PDF, OUTPUT_DPI, SPACING_MM)