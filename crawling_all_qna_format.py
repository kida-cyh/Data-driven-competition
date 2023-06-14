import urllib.request
from bs4 import BeautifulSoup
import json
import re

qna_list = []
crawling_count = 0
pass_count = 0
all_count = 0

try:
    first_url = "https://terms.naver.com/list.naver?cid=63166&categoryId=63166"
    print("Crawling Start")
    data = urllib.request.urlopen(first_url)
    soup = BeautifulSoup(data, "html.parser")
    column_index = 0
    
    # 링크 목록 추출
    link_list = soup.find_all("li", class_="subject_item")
    links = []

    for li in link_list:
        for a_tag in li.find_all("a", href=True):
            links.append(a_tag["href"])

    for link in links:
        link_url = "https://terms.naver.com" + link
        column_index += 1
        print("column_index:", column_index)
        print("link_url:", link_url)
        #qna 형태 크롤링만 여기서 한다.
        if column_index in {2, 3, 4, 5, 6, 7, 8, 9, 11, 12, 13, 14, 15, 16}:
            continue

        try:
            base_url = link_url + "&page="
            page = 1

            while True:
                url = base_url + str(page)
                print("Crawling page", page)
                data = urllib.request.urlopen(url)
                soup = BeautifulSoup(data, "html.parser")

                # 링크 목록 추출
                link_list = soup.find_all("strong", class_="title")
                links = []

                for ul in link_list:
                    for a_tag in ul.find_all("a", href=True):
                        if a_tag["href"] != "#":
                            if a_tag["href"] != "/tlist":
                                links.append(a_tag["href"])

                # 링크에 접속하여 정보 추출
                for link in links:
                    link_url = "https://terms.naver.com" + link

                    try:
                        link_data = urllib.request.urlopen(link_url)
                        link_soup = BeautifulSoup(link_data, "html.parser")

                        # 질문 추출
                        question_elements = link_soup.find_all("p", class_="txt")
                        question_list = []
                        for question_element in question_elements:
                            question_text = question_element.text.strip()
                            if question_text.startswith("Q."):
                                question = question_text[2:].strip()
                                question_list.append(question)

                        # 답변 추출
                        answer_elements = link_soup.find_all("p", class_="txt")
                        answer_list = []
                        for answer_element in answer_elements:
                            answer_text = answer_element.text.strip()
                            if answer_text.startswith("A."):
                                answer = answer_text[2:].strip()
                                answer_list.append(answer)

                        # 질문과 답변이 모두 있는 경우에만 전체 텍스트를 저장
                        if len(question_list) == len(answer_list):
                            for question, answer in zip(question_list, answer_list):
                                qna_dict = {'instruction': question, 'input': '', 'output': answer}
                                qna_list.append(qna_dict)
                                crawling_count += 1
                        else:
                            pass_count += 1
                
                    except Exception as e:
                        print("예외 발생:", str(e))
                        continue
                
                 # 다음 페이지로 이동
                next_page_link = soup.find("span", class_="next disabled")
                if next_page_link:
                    break  # 다음 페이지가 없으면 반복 종료
                page += 1
                
        except Exception as e:
            print("예외 발생:", str(e))
            pass 

except Exception as e:
    print("예외 발생:", str(e))
    pass

except:
    pass

# JSON 파일로 저장
with open('qna_data_qna_format.json', 'w', encoding='utf-8') as file:
    json.dump(qna_list, file, ensure_ascii=False, indent=4)

print('All_count:', all_count)
print('Crawling_count:', crawling_count)
print('Pass_count:', pass_count)
print('JSON 파일 생성이 완료되었습니다.')
