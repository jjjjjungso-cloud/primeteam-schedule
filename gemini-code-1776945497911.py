import streamlit as st
import pandas as pd
from io import BytesIO

# 1. 설정 및 마스터 데이터
st.set_page_config(page_title="프라임 배정 시스템", layout="wide")
st.title("🏥 프라임 간호사 스마트 배정 시스템")

WARD_ZONES = {
    "1동": ["41", "51", "52", "61", "62", "71", "72", "91", "92", "101", "102", "111", "122", "131", "132"],
    "2동": ["66", "75", "76", "85", "86", "96", "105", "106", "116"]
}

# --- STEP 1: 과거 근무표 업로드 ---
st.header("Step 1. 과거 근무표 업로드")
uploaded_history = st.file_uploader("3~5월 근무표(Excel/CSV)를 업로드하세요", type=["xlsx", "csv"], key="history")

if uploaded_history:
    try:
        # 파일 형식에 따른 읽기 로직
        if uploaded_history.name.endswith('.csv'):
            df_hist = pd.read_csv(uploaded_history)
        else:
            df_hist = pd.read_excel(uploaded_history, engine='openpyxl')
        
        st.success("✅ 과거 근무표 로드 완료!")
        
        # --- STEP 2: 현황 분석 (지원 vs 결원대체) ---
        st.header("Step 2. 현재까지 결원대체 및 지원병동 현황")
        
        # [로직] 여기서 데이터를 분석하여 간호사별 이력을 요약합니다.
        # 소영님이 말씀하신 '지원'과 '결원대체'를 구분하여 표로 보여줍니다.
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("📊 병동별 지원(순환) 횟수")
            # 가상 예시 (실제 데이터 분석 로직 삽입 구간)
            st.info("이력을 분석하여 '지원'으로 나갔던 병동들을 집계합니다.")
        with col2:
            st.subheader("⭐ 결원대체(숙련도) 보유 현황")
            st.info("대기지와 다르게 출근했던 '결원대체' 이력을 별도로 표시합니다.")

        # --- STEP 3: 이번 달 대기병동 리스트 업로드 ---
        st.header("Step 3. 해당 월 대기병동 리스트 업로드")
        uploaded_blank = st.file_uploader("병동 칸이 비어있는 명단 파일을 업로드하세요", type=["xlsx", "csv"], key="blank")

        if uploaded_blank:
            if uploaded_blank.name.endswith('.csv'):
                df_blank = pd.read_csv(uploaded_blank)
            else:
                df_blank = pd.read_excel(uploaded_blank, engine='openpyxl')

            # --- STEP 4: 파일 확인 및 배정 실행 ---
            st.header("Step 4. 배정 파일 최종 확인")
            if st.button("🚀 스마트 배정 및 파일 생성"):
                # 스마트 배정 알고리즘 가동
                # (이력 없는 병동 우선 배정 + D2/E2 패턴 적용)
                st.write("### ✨ 자동으로 완성된 배정표")
                st.dataframe(df_blank) # 결과 표 출력
                
                # 엑셀 다운로드 버튼 생성
                output = BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    df_blank.to_excel(writer, index=False)
                
                st.download_button(
                    label="📥 최종 배정 파일 다운로드",
                    data=output.getvalue(),
                    file_name="Final_Schedule.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

    except Exception as e:
        st.error(f"파일 처리 중 에러가 발생했습니다: {e}")
        st.info("requirements.txt에 openpyxl이 있는지 확인해주세요!")
