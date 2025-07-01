# 📄 PNG to PDF Converter

여러 개의 PNG 이미지 파일을 하나의 A4 사이즈 PDF 문서로 변환해주는 간단하고 강력한 웹 애플리케이션입니다. Streamlit을 사용하여 제작되었습니다.

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)]([https://your-app-url.streamlit.app](https://sheetmusic-png2pdf-hmheeu3c62wa2bemmyoyoa.streamlit.app/) 

---

## ✨ 주요 기능

- **다중 파일 업로드**: 여러 개의 PNG 파일을 한 번에 업로드할 수 있습니다.
- **A4 PDF 변환**: 업로드된 모든 이미지를 순서대로 병합하여 하나의 A4 사이즈 PDF 파일로 생성합니다.
- **자동 정렬**: 파일 이름에 포함된 숫자를 인식하여 `1, 2, ... 10` 순서로 정확하게 정렬합니다.
- **자동 DPI 감지**: 각 이미지의 DPI 메타데이터를 자동으로 읽어와 최적의 크기로 조절합니다.
- **사용자 맞춤 설정**:
    - **출력 해상도(DPI)**: 생성될 PDF의 전체적인 품질을 조절할 수 있습니다.
    - **이미지 간 여백**: 이미지와 이미지 사이의 세로 간격을 mm 단위로 설정할 수 있습니다.
    - **세로 크기 고정**: 가로가 좁은 이미지가 과도하게 확대되는 것을 방지하고, 모든 이미지의 높이를 일관되게 유지하는 옵션을 제공합니다.
- **실시간 미리보기**: 생성된 PDF를 다운로드하기 전에 웹 화면에서 바로 내용을 확인할 수 있습니다.

---

## 🚀 사용법

### 1. 웹 애플리케이션으로 사용하기

배포된 Streamlit Community Cloud 링크에 접속하여 바로 사용할 수 있습니다.

1.  웹 페이지의 업로드 영역에 PNG 파일들을 드래그 앤 드롭하거나 클릭하여 선택합니다.
2.  왼쪽 사이드바에서 원하는 PDF 설정을 조절합니다.
3.  `PDF 생성하기` 버튼을 클릭합니다.
4.  생성된 PDF를 미리보기로 확인하고 `PDF 다운로드` 버튼을 눌러 저장합니다.

### 2. 로컬 환경에서 실행하기

이 프로젝트를 직접 컴퓨터에서 실행하고 싶다면 아래 단계를 따르세요.

**사전 준비물:**
- [Python 3.8 이상](https://www.python.org/downloads/)

**설치 및 실행:**

1.  **저장소 복제:**
    ```bash
    git clone [https://github.com/your-username/your-repository-name.git](https://github.com/your-username/your-repository-name.git)
    cd your-repository-name
    ```

2.  **필요한 라이브러리 설치:**
    프로젝트 폴더에 포함된 `requirements.txt` 파일을 사용하여 필요한 라이브러리를 설치합니다.
    ```bash
    pip install -r requirements.txt
    ```

3.  **Streamlit 앱 실행:**
    터미널에서 아래 명령어를 실행합니다.
    ```bash
    streamlit run app.py
    ```
    명령어를 실행하면 자동으로 웹 브라우저 창이 열리며 애플리케이션이 나타납니다.

---

## 📂 파일 구성


.
├── app.py              # 메인 Streamlit 애플리케이션 코드
├── requirements.txt    # 필요한 Python 라이브러리 목록
└── README.md           # 프로젝트 설명 파일


---

## 🛠️ 설정 옵션 상세

- **세로 크기 고정 (두 번째 이미지 기준)**: 이 옵션을 선택하면,
    1.  두 번째 이미지의 높이를 기준으로 모든 이미지의 최대 높이가 제한됩니다.
    2.  기준보다 세로가 긴 이미지는 축소되고, 작은 이미지는 확대되지 않습니다.
    3.  이를 통해 가로가 좁은 이미지가 불필요하게 커지는 것을 막아 일관된 보기 환경을 제공합니다.
    4.  모든 이미지는 왼쪽에 정렬됩니다.
- **출력 PDF 해상도 (DPI)**: PDF 문서의 인치당 도트 수입니다. 값이 높을수록 이미지가 선명해지지만 파일 크기가 커집니다. (기본값: 300)
- **이미지 사이 여백 (mm)**: PDF 페이지 내에서 각 이미지의 상하 간격을 밀리미터 단위로 조절합니다. (기본값: 0)
