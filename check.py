import json
import re

def count_lines_without_special_chars(json_code):
    lines = json_code.split('\n')
    count = 0
    for line in lines:
        line = re.sub('[^a-zA-Z0-9ㄱ-ㅎ가-힣\s]', '', line)
        if line.strip():
            count += 1
    return count

# JSON 코드를 불러옵니다.
with open('total_qna_data.json', 'r', encoding='utf-8') as file:
    json_code = file.read()

# 특수 문자를 제외한 라인 수를 계산합니다.
line_count = count_lines_without_special_chars(json_code)

# 결과 출력
print("특수 문자를 제외한 라인 수:", line_count)
