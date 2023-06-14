# 네이버 건강검진 QnA 페이지 스크래핑
import urllib.request
from bs4 import BeautifulSoup
import time
import json

qna_list = []

try:
    url = "https://terms.naver.com/list.naver?cid=66631&categoryId=66631"
    print(url)
    data = urllib.request.urlopen(url)
    soup = BeautifulSoup(data, "html.parser")

    # 링크 목록 추출
    link_list = soup.find_all("ul", class_="contents_list")
    links = []
    for ul in link_list:
        links.extend(ul.find_all("a", href=True))

    # 링크에 접속하여 정보 추출
    for link in links:
        link_url = "https://terms.naver.com" + link["href"]  # 링크의 절대 주소 생성
        print(link_url)

        try:
            # 링크에 접속하여 제목과 요약 추출
            link_data = urllib.request.urlopen(link_url)
            link_soup = BeautifulSoup(link_data, "html.parser")

            # 질문 추출
            question_element = link_soup.find("p", class_="txt", string=lambda text: text and text.startswith("Q."))
            question = question_element.text.strip()[2:] if question_element else ""

            # 답변 추출
            answer_element = link_soup.find("p", class_="txt", string=lambda text: text and text.startswith("A."))
            answer = answer_element.text.strip()[2:] if answer_element else ""

            # 질문과 답변을 딕셔너리 형태로 저장
            qna_dict = {'instruction': question, 'input': '', 'output': answer}
            qna_list.append(qna_dict)

            print("-----")

            # 링크 접속 딜레이
            #time.sleep(1)

        except Exception as e:
            print("예외 발생:", str(e))
            continue

except Exception as e:
    print("예외 발생:", str(e))
    pass

except:
    pass

# JSON 파일로 저장
with open('qna_data_health_check.json', 'w', encoding='utf-8') as file:
    json.dump(qna_list, file, ensure_ascii=False, indent=4)

print('JSON 파일 생성이 완료되었습니다.')
