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
st.header("Step 1. 데이터 업로드 (과거 계획 vs 실제 근무)")
col_u1, col_u2 = st.columns(2)
with col_u1:
    uploaded_plan = st.file_uploader("1. 과거 대기병동 배정표(계획)", type=["xlsx", "csv"])
with col_u2:
    uploaded_actual = st.file_uploader("2. 실제 근무스케줄표(결과)", type=["xlsx", "csv"])

if uploaded_plan and uploaded_actual:
    try:
        # 데이터 읽기
        df_p = pd.read_excel(uploaded_plan) if uploaded_plan.name.endswith('.xlsx') else pd.read_csv(uploaded_plan)
        df_a = pd.read_excel(uploaded_actual) if uploaded_actual.name.endswith('.xlsx') else pd.read_csv(uploaded_actual)
        
        # --- STEP 2: 현황 분석 (여기가 핵심 로직입니다!) ---
        st.header("Step 2. 현재까지 결원대체 및 지원병동 현황")
        
        # 분석 결과를 담을 딕셔너리
        history = {} # {이름: {'지원': [], '결원대체': []}}

        # [핵심 수식] 이름별로 계획과 실제를 비교
        for name in df_p['이름'].unique():
            p_ward = str(df_p[df_p['이름'] == name]['배정병동'].values[0])
            # 실제 근무표에서 해당 이름의 근무지 추출 (P-D63/116 형태에서 번호만 추출)
            a_ward_raw = str(df_a[df_a['이름'] == name]['근무지'].values[0])
            a_ward = re.findall(r'\d+', a_ward_raw)[0] if re.findall(r'\d+', a_ward_raw) else ""

            if name not in history: history[name] = {'지원': [], '결원대체': []}
            
            if p_ward == a_ward:
                history[name]['지원'].append(a_ward)
            else:
                history[name]['결원대체'].append(a_ward)

        # 현황 시각화
        st.write("### 📋 간호사별 누적 이력 요약")
        st.table(pd.DataFrame.from_dict(history, orient='index'))

        # --- STEP 3: 이번 달 대기병동 리스트 업로드 ---
        st.header("Step 3. 해당 월 대기병동 리스트 업로드")
        uploaded_blank = st.file_uploader("이번 달 빈 명단 파일을 업로드하세요", type=["xlsx", "csv"])

        if uploaded_blank:
            df_blank = pd.read_excel(uploaded_blank) if uploaded_blank.name.endswith('.xlsx') else pd.read_csv(uploaded_blank)
            
            # D4 전담자 선택 기능 추가
            st.subheader("🗓️ 특수 근무 설정")
            d4_target = st.multiselect("이번 달 D4(한 달 오전) 근무자를 선택하세요", df_blank['이름'].unique())

            # --- STEP 4: 스마트 배정 실행 ---
            st.header("Step 4. 배정 파일 최종 확인")
            if st.button("🚀 스마트 배정 실행"):
                
                for idx, row in df_blank.iterrows():
                    name = row['이름']
                    building = row['소속'] # '1동' 또는 '2동'
                    
                    # 1. D4 전담자라면?
                    if name in d4_target:
                        df_blank.at[idx, '배정결과'] = "P-D63/(D4고정)"
                    # 2. 일반 순환이라면? (지원 이력 없는 병동 추천)
                    else:
                        candidates = WARD_ZONES.get(building, [])
                        visited = history.get(name, {}).get('지원', [])
                        # 안 가본 곳 필터링
                        not_visited = [w for w in candidates if w not in visited]
                        recommended = not_visited[0] if not_visited else candidates[0]
                        df_blank.at[idx, '배정결과'] = f"P-D63/{recommended}"

                st.write("### ✨ 자동으로 완성된 배정표")
                st.dataframe(df_blank)
                
                # 엑셀 다운로드
                output = BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    df_blank.to_excel(writer, index=False)
                st.download_button("📥 최종 배정 파일 다운로드", output.getvalue(), "Final_NSS.xlsx")

    except Exception as e:
        st.error(f"오류 발생: {e}. 파일의 '이름', '배정병동' 컬럼명을 확인해주세요.")
