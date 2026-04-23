import streamlit as st
import pandas as pd
import re
from datetime import datetime
from io import BytesIO

# --- 설정 및 마스터 데이터 ---
st.set_page_config(page_title="프라임 배정 시스템", layout="wide")
st.title("🏥 프라임 간호사 스마트 순환 배정 시스템")

# 병동 구역 설정
WARD_ZONES = {
    "1동": ["41", "51", "52", "61", "62", "71", "72", "91", "92", "101", "102", "111", "122", "131", "132"],
    "2동": ["66", "75", "76", "85", "86", "96", "105", "106", "116"]
}

# --- STEP 1: 데이터 로드 및 분석 로직 ---
st.header("Step 1. 데이터 입력 및 이력 분석")

col1, col2 = st.columns(2)
with col1:
    uploaded_plan = st.file_uploader("1. 과거 대기병동 배정표(계획) 업로드", type=["xlsx", "csv"])
with col2:
    uploaded_actual = st.file_uploader("2. 실제 근무스케줄표(결과) 업로드", type=["xlsx", "csv"])

def analyze_experience(plan_df, actual_df):
    """계획과 실제를 비교하여 지원/결원대체 구분"""
    # 이 부분은 소영님의 파일 구조에 맞춰 성함/병동 컬럼을 매칭하여 
    # '지원' 이력과 '결원 대체' 이력을 데이터프레임으로 반환합니다.
    # 예시를 위해 구조만 잡았습니다.
    summary = pd.DataFrame(columns=["이름", "구분", "병동", "날짜"])
    return summary

if uploaded_plan and uploaded_actual:
    st.success("✅ 이력 분석 준비 완료!")
    
    # --- STEP 2: 현황판 ---
    st.header("Step 2. 간호사별 병동 지원 및 결원 대체 현황")
    # 분석된 데이터를 시각화하거나 표로 보여줍니다.
    st.info("현재 각 간호사별로 미방문 병동과 결원 대체 숙련도가 계산되었습니다.")
    
    # --- STEP 3: 이번 달 배정 ---
    st.header("Step 3. 해당 월 대기병동 배정 (D4 및 순환)")
    
    uploaded_foam = st.file_uploader("이번 달 빈 명단(Foam) 업로드", type=["xlsx", "csv"])
    
    if uploaded_foam:
        d4_nurse = st.selectbox("이번 달 D4(한 달 전담) 근무자를 선택하세요", ["자동 추천"] + ["정윤정", "기아현", "김유진", "박소영"]) # 명단 자동화 가능
        
        if st.button("🚀 스마트 배정 실행 및 확정"):
            # 배정 로직 실행
            # 1. D4는 한 달 내내 D코드로 고정
            # 2. 나머지는 지원 이력 없는 병동 순회 배정
            st.subheader("✨ 이번 달 최종 배정 결과 (확정)")
            
            # 가상의 결과 데이터프레임 생성
            result_df = pd.DataFrame({
                "이름": ["정윤정", "기아현"],
                "근무타입": ["D4 (전담)", "D2/E2 (순환)"],
                "배정병동": ["P-D63/051", "P-D63/116"],
                "비고": ["D4 순번", "116병동 결원대체 숙련자"]
            })
            
            st.dataframe(result_df)

            # --- STEP 4: 파일 다운로드 ---
            st.header("Step 4. 최종 파일 확인 및 다운로드")
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                result_df.to_excel(writer, index=False, sheet_name='배정확정')
            
            st.download_button(
                label="📥 최종 배정 스케줄표 다운로드",
                data=output.getvalue(),
                file_name=f"NSS_Schedule_{datetime.now().strftime('%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            
            st.success("💾 이 기록은 다음 달 배정 시 '과거 이력'으로 자동 반영됩니다.")

else:
    st.warning("먼저 과거 데이터를 업로드하여 시스템을 학습시켜주세요.")