# 국가중점데이터 질의응답 변환
# 가입자일련번호와 질병코드 중복되는 데이터 삭제 후 데이터 처리
import pandas as pd
import json

# 진료기록 데이터셋 읽기
df_medi_charts1= pd.read_excel('T20_2019_1-1.xlsx')
df_medi_charts2 = pd.read_excel('T20_2019_1-2.xlsx')
df_medi_charts3 = pd.read_excel('T20_2019_1-3.xlsx')
df_medi_charts = pd.concat([df_medi_charts1, df_medi_charts2, df_medi_charts3], ignore_index=True)

# 중복된 질병코드와 사용자 ID를 제거하여 유니크한 값 유지
df_medi_charts = df_medi_charts.sort_values(by=['가입자 일련번호', '요양개시일자'], ascending=True)
df_medi_charts = df_medi_charts.drop_duplicates(subset=['주상병코드', '가입자 일련번호'], keep='first')
df_medi_charts.to_excel('result_chart.xlsx', index=False)

# 질병코드 데이터셋 읽기
df_disease_code = pd.read_excel('disease_code.xlsx')

# 중복된 주상병코드 제거하여 유니크한 값 유지
df_disease_code_unique = df_disease_code.drop_duplicates(subset='주상병코드', keep='first')

# 질병명 맵핑을 위한 딕셔너리 생성
disease_mapping = df_disease_code_unique.set_index('주상병코드')['한글명칭'].to_dict()

# '주상병코드'에 해당하는 한글명칭 찾아 맵핑
df_medi_charts['주상병명'] = df_medi_charts['주상병코드'].map(disease_mapping)

# 요양개시일에서 월을 분리
df_medi_charts['발병월'] = df_medi_charts['요양개시일자'].astype(str).str.slice(4, 6)
df_medi_charts['발병월'] = df_medi_charts['발병월'].astype(str).str.lstrip('0')


# 성별코드에 대한 맵핑 딕셔너리 생성
gender_mapping = {1: '남자', 2: '여자'}

# 연령코드에 대한 맵핑 딕셔너리 생성
age_mapping = {1: '0~4세', 2: '5~9세', 3: '10~14세', 4: '15~19세', 5: '20~24세', 6: '25~29세', 7: '30~34세', 8: '35~39세', 9: '40~44세',
               10: '45~49세', 11: '50~54세', 12: '55~59세',  13: '60~64세', 14: '65~69세', 15: '70~74세', 16: '75~79세', 17: '80~84세', 18: '85세 이상'}

# 지역코드에 대한 맵핑 딕셔너리 생성
location_mapping = {11: '서울', 26: '부산', 27: '대구', 28: '인천', 29: '광주', 30: '대전', 31: '울산', 36: '세종',
                 41: '경기도', 42: '강원도', 43: '충북', 44: '충남', 45: '전북', 46: '전남', 47: '경북', 48: '경남', 49: '제주'}
try:
    # 주상병명 전체 빈도 계산
    total_frequency = df_medi_charts['주상병명'].value_counts().reset_index()
    total_frequency.columns = ['주상병명', '질병발생빈도']
    total_frequency = total_frequency.sort_values('주상병명', ascending=True)

    # 주상병명 평균 입내원 일수
    # average_length_of_stay = df_medi_charts.groupby('주상병명')['입내원일수'].mean().reset_index()
    # average_length_of_stay['평균입내원일수'] = average_length_of_stay['입내원일수'].round().astype(int)
    # average_length_of_stay = average_length_of_stay.drop('입내원일수', axis=1)
    # average_length_of_stay = average_length_of_stay.sort_values('주상병명', ascending=True)
    # merged_df = pd.merge(total_frequency, average_length_of_stay, on='주상병명')
    
    # 주상병명과 성별코드로 그룹화하여 성별별 주상병명의 빈도 계산
    gender_grouped = df_medi_charts.groupby(['주상병명', '성별코드']).size().reset_index(name='성별빈도')    
    gender_idx = gender_grouped.groupby('주상병명')['성별빈도'].transform(max) == gender_grouped['성별빈도']
    most_common_genders = gender_grouped[gender_idx].groupby('주상병명').first().reset_index()
    merged_df = pd.merge(total_frequency, most_common_genders, on='주상병명')

    # 주상병명과 연령코드로 그룹화하여 나이별 주상병명의 빈도 계산
    age_grouped = df_medi_charts.groupby(['주상병명', '연령대코드']).size().reset_index(name='연령대빈도')
    age_idx = age_grouped.groupby('주상병명')['연령대빈도'].transform(max) == age_grouped['연령대빈도']
    most_common_age = age_grouped[age_idx].groupby('주상병명').first().reset_index()
    merged_df = pd.merge(merged_df, most_common_age, on='주상병명')

    # 주상병명과 지역코드로 그룹화하여 지역별 주상병명의 빈도 계산
    location_grouped = df_medi_charts.groupby(['주상병명', '시도코드']).size().reset_index(name='시도빈도')    
    location_idx = location_grouped.groupby('주상병명')['시도빈도'].transform(max) == location_grouped['시도빈도']
    most_common_location = location_grouped[location_idx].groupby('주상병명').first().reset_index()
    merged_df = pd.merge(merged_df, most_common_location, on='주상병명')

    # 주상병명과 발병월로 그룹화하여 월별 주상병명의 빈도 계산
    month_grouped = df_medi_charts.groupby(['주상병명', '발병월']).size().reset_index(name='발병월빈도')    
    month_idx = month_grouped.groupby('주상병명')['발병월빈도'].transform(max) == month_grouped['발병월빈도']
    most_common_month = month_grouped[month_idx].groupby('주상병명').first().reset_index()
    merged_df = pd.merge(merged_df, most_common_month, on='주상병명')

    # 전체 빈도 대비 빈도 높은 성별의 비율 계산하여 컬럼 추가
    merged_df['비중'] = round(merged_df['성별빈도'] / merged_df['질병발생빈도'] * 100).astype(int)
    
    merged_df.to_excel('merge_chart.xlsx', index=False)

    qna_list = []
    #결과 출력
    for index, row in merged_df.iterrows():
        disease_frequency = row['질병발생빈도']
        disease_name = row['주상병명']
        gender_code = row['성별코드']
        # average_stay = row['평균입내원일수']
        gender_percentage = row['비중']
        age_code = row['연령대코드']
        location_code = row['시도코드']
        location_frequency = row['시도빈도']
        month = row['발병월']    
        month_frequency = row['발병월빈도']    
        gender = gender_mapping.get(gender_code, '알 수 없음')
        age = age_mapping.get(age_code, '알 수 없음')
        location = location_mapping.get(location_code, '알 수 없음')

        # 질문 추출
        question = f"{disease_name}의 발생현황과 진료현황에 대해 설명해줘"        
        # 답변 추출         
        answer = f"2019년 기준으로 {disease_name}는 {disease_frequency}명의 환자가 발생하였습니다. 전체 환자 중 {gender_percentage}%가 {gender}환자이며, 연령대 별로는 {age}가 지역별로는 {location}지역에서 가장 많은 환자가 보고되었고, 월별로는 {month}월에 {month_frequency}명으로 발병이 가장 많았습니다. "

        # 질문과 답변을 딕셔너리 형태로 저장
        qna_dict = {'instruction': question, 'input': '', 'output': answer}
        qna_list.append(qna_dict)   

except Exception as e:
    print("예외 발생:", str(e))
    pass

except:
    pass

#JSON 파일로 저장
with open('opendata_qna_list_new.json', 'w', encoding='utf-8') as file:
    json.dump(qna_list, file, ensure_ascii=False, indent=4)

print('JSON 파일 생성이 완료되었습니다.')
# 결과 확인
# merged_df.to_excel('merge_chart.xlsx', index=False)
# df_medi_charts.to_excel('result_chart.xlsx', index=False)