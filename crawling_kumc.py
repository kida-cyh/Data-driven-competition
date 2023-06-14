import urllib.request
from bs4 import BeautifulSoup
import json

qna_list = []

try:
    base_url = "https://terms.naver.com/list.naver?cid=63166&categoryId=59314&page="
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
                    links.append(a_tag["href"])

        # 링크에 접속하여 정보 추출
        for link in links:
            link_url = "https://terms.naver.com" + link

            try:
                link_data = urllib.request.urlopen(link_url)
                link_soup = BeautifulSoup(link_data, "html.parser")

                # 질문과 답변 추출
                e_questions = link_soup.find_all("div", class_="na_block_quote")
                e_answers = link_soup.find_all('p', class_='se_textarea')

                if e_questions and e_answers:
                    questions = [question.get_text(strip=True) for question in e_questions]
                    answers = [answer.get_text(strip=True) for answer in e_answers]

                    # 질문과 답변을 짝지어서 저장
                    for question, answer in zip(questions, answers):
                        if question and answer:
                            qna_dict = {'instruction': question, 'input': '', 'output': answer}
                            qna_list.append(qna_dict)

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

except:
    pass

# JSON 파일로 저장
with open('qna_data_kumc.json', 'w', encoding='utf-8') as file:
    json.dump(qna_list, file, ensure_ascii=False, indent=4)

print('JSON 파일 생성이 완료되었습니다.')
