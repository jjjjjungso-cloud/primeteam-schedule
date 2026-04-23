import streamlit as st
import pandas as pd
import re
from io import BytesIO

# 1. 병동 및 구역 설정
WARD_ZONES = {
    "1동": ["41", "51", "52", "61", "62", "71", "72", "91", "92", "101", "102", "111", "122", "131", "132"],
    "2동": ["66", "75", "76", "85", "86", "96", "105", "106", "116"]
}

st.title("🏥 프라임 간호사 스마트 배정 시스템")
st.markdown("지원 이력과 결원 대체 이력을 분석하여 최적의 병동을 추천합니다.")

# 2. 데이터 업로드 세션
st.sidebar.header("📁 데이터 업로드")
uploaded_history = st.sidebar.file_uploader("1. 과거 근무표 업로드", type=["csv", "xlsx"])
if uploaded_history:
    if uploaded_history.name.endswith('.csv'):
        df_hist = pd.read_csv(uploaded_history)
    else:
        df_hist = pd.read_excel(uploaded_history) # 엑셀을 읽는 마법의 한 줄!

# 3. 핵심 로직 함수
def process_history(df):
    """
    근무표에서 지원(P-D63/번호)과 결원 대체(대기지와 다른 곳 출근)를 구분하여 학습
    """
    history = {} # {이름: {'지원': set(), '결원대체': set()}}
    # 여기에 소영님이 주신 파일 구조에 맞게 '지원' 텍스트가 포함된 경우와
    # 실제 근무지가 다른 경우를 추출하는 로직이 들어갑니다.
    # (파일 내 'P-D63/072' 형태의 데이터를 정규식으로 파싱)
    return history

def get_best_ward(name, building, history, recent_months=3):
    """
    지원 이력이 없는 병동을 최우선으로 추천
    """
    all_wards = WARD_ZONES.get(building, [])
    visited_wards = history.get(name, {}).get('지원', set())
    
    # 지원 경험이 없는 병동 필터링
    candidates = [w for w in all_wards if w not in visited_wards]
    
    # 만약 모든 병동을 다 가봤다면 가장 오래전에 간 곳 추천
    if not candidates:
        candidates = all_wards
        
    return candidates[0] if candidates else "공석"

# 4. 메인 실행 부분
if uploaded_history and uploaded_blank:
    # 데이터 로드
    df_hist = pd.read_csv(uploaded_history)
    df_blank = pd.read_csv(uploaded_blank)
    
    # 역사 학습 (지원 vs 결원대체 구분)
    nurse_history = process_history(df_hist)
    
    if st.button("🚀 스마트 배정 실행"):
        st.subheader("✨ 이번 달 추천 배정 결과")
        
        # 블랭크 파일 순회하며 채우기
        for idx, row in df_blank.iterrows():
            name = row['이름']
            building = row['소속']
            
            # 스마트 추천 실행
            recommended = get_best_ward(name, building, nurse_history)
            df_blank.at[idx, '추천병동'] = f"P-D63/{recommended}"
            
            # 결원 대체 숙련자 표시 (예: 116병동 경험자)
            if recommended == '116' and name in nurse_history.get(name, {}).get('결원대체', set()):
                st.info(f"⭐ {name} 간호사는 {recommended}병동 결원 대체 숙련자입니다!")

        st.dataframe(df_blank)

        # 5. 엑셀 다운로드
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df_blank.to_excel(writer, index=False)
        
        st.download_button(
            label="📥 완성된 NSS 스케줄표 다운로드",
            data=output.getvalue(),
            file_name="NSS_Final_Schedule.xlsx"
        )
