import json
import re

with open('total_qna_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

qna_list = []
pattern = r'(Q\..*?)\s*(A\..*?)(?=\s*Q\.|$)'

for item in data:
    output_data = item['output']
    matches = re.findall(pattern, output_data, flags=re.DOTALL)

    for match in matches:
        question = match[0].strip()
        answer = match[1].strip()
        qna_list.append((question, answer))

# 예시 출력
for qna in qna_list:
    print(qna)