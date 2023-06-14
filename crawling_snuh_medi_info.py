import urllib.request
from bs4 import BeautifulSoup
import json

qna_list = []
crawling_count = 0
pass_count = 0
all_count = 0
try:
    base_url = "https://terms.naver.com/list.naver?cid=51007&categoryId=51007&page="
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
        #print(links)
        # 링크에 접속하여 정보 추출
        for link in links:
            link_url = "https://terms.naver.com" + link

            try:
                link_data = urllib.request.urlopen(link_url)
                link_soup = BeautifulSoup(link_data, "html.parser")

                # 질문추출
                #질병명 추출
                e_disease_name = link_soup.find("h2", class_="headword")
                disease_name = e_disease_name.text.strip() + '의'
                #서브제목 추출
                e_sub_titles = link_soup.find_all("h3", class_="stress")
                #질문 조합 (질병명 + '의' + 서브제목 + '이/가 뭔가요?')               
                question_list = []
                for e_sub_title in e_sub_titles:
                    #question_text = disease_name + ' ' + e_sub_title.text.strip() + '이/가 뭔가요?'
                    question_text = e_sub_title.text.strip()
                    if question_text in {'정의','검사주기','결과'}:
                        question_text = disease_name + " "  + question_text + "는 어떻게 되나요?"
                    elif question_text in {'원인','증상','예방방법','소요시간','진단질병','치료질병'}:
                        question_text = disease_name + " "  + question_text + "은 어떻게 되나요?"
                    elif question_text == '진단/검사':
                        question_text = disease_name + " "  + "진단 및 검사 방법은 어떻게 되나요?"
                    elif question_text == '치료':
                        question_text = disease_name + " "  + question_text + "방법은 어떻게 되나요?"
                    elif question_text == '경과/합병증':
                        question_text = disease_name + " "  + "경과 및 합병증은 어떻게 되나요?"
                    elif question_text == '부작용/후유증':
                        question_text = disease_name + " "  + "부작용 및 후유증은 어떻게 되나요?"
                    elif question_text == '식이요법/생활가이드':
                        question_text = disease_name + " "  + "식이요법 및 생활가이드는 어떻게 될까요?"
                    elif question_text in {'관련질병','하위질병','검사방법', '주의사항','관련검사법','시술방법','관련치료법'}:
                        question_text = disease_name + " "   + question_text + "은 어떤것들이 있나요?"
                    elif question_text in {'종류','생활가이드'}:
                        question_text = disease_name + " "   + question_text + "는 어떤것들이 있나요?"
                    else:
                        question_text = disease_name
                    question_list.append(question_text)
        
                # file_path = 'questions.txt'
                # with open(file_path, 'a', encoding='utf-8') as file:
                #     for question in question_list:
                #         file.write(question + '\n')                
                #print(question_list)
                #답변 추출
                answer_elements = link_soup.find_all("p", class_="txt")
                answer_list = []
                for answer_element in answer_elements:
                    answer_text = answer_element.text.strip()
                    answer_list.append(answer_text)
                
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

except:
    pass

# JSON 파일로 저장
with open('qna_data_sunh_medi_info.json', 'w', encoding='utf-8') as file:
    json.dump(qna_list, file, ensure_ascii=False, indent=4)

print('JSON 파일 생성이 완료되었습니다.')
print('All_count:', all_count)
print('Crawling_count:', crawling_count)
print('Pass_count:', pass_count)
print('JSON 파일 생성이 완료되었습니다.')
