import re
import json
import base64
import time
import requests
from bs4 import BeautifulSoup

questions = []

def get_correct_answer(url, script):
    questionNumber = url.split("/")[-1]

    pattern = r'bc\d+\("([^"]*)"\)'
    match = re.search(pattern, script)
    
    if match:
        encoded_text = match.group(1)
        char = int(base64.b64decode(encoded_text).decode()) - int(questionNumber)
        return chr(char)
    return None

def parse_question_page(url, topic):
    baseurl = "https://www.bomcondutor.pt"

    response = requests.get(url)
    page = response.text

    soup = BeautifulSoup(page, "html.parser")
    script = soup.find_all("script")
    correctAnwser = None
    for src in script:
        if "correct" in src.text:
            correctAnwser = get_correct_answer(url, src.text.strip())

    image = soup.find("img", class_="question-image")
    if image:
        image_url = baseurl+image["src"]
        image_response = requests.get(image_url)
        image_name = image_url.split("/")[-1]
        with open(f"images/{topic}_{image_name}", "wb") as file:
            file.write(image_response.content)

    question = soup.find("div", class_="question-text")
    question_text = question.find("div", class_="text").text
    print(question_text.strip())

    answer_data = []
    answers = soup.find_all("li", class_="answer")
    for answer in answers:
        answer_class = answer["class"]
        is_correct = correctAnwser in answer_class
        answer_text = answer.find("span", class_="answer-text").text.strip()
        answer_data.append({
            "text": answer_text,
            "correct": is_correct
        })

        
    answers_data = {
        "question": question_text.strip(),
        "image": f"images/{topic}_{image_name}" if image else None,
        "answers": answer_data
    }

    if is_correct:
        print("*", end="")
    print(answer_text)
    
    questions.append(answers_data)
        

def get_question_links(url):
    baseurl = "https://www.bomcondutor.pt"

    response = requests.get(url)
    page = response.text

    soup = BeautifulSoup(page, "html.parser")
    links = soup.find_all("span", class_="question")

    topic = url.split("/")[-1]

    for link in links:
        link = link.find("a")
        parse_question_page(baseurl + link["href"], topic)

    with open(f"{topic}.json", "w") as file:
        json.dump(questions, file, indent=4)
    time.sleep(5)
    questions.clear()


def main():
    baseurl = "https://www.bomcondutor.pt"
    url = "https://www.bomcondutor.pt/questoes/B"

    response = requests.get(url)
    page = response.text

    soup = BeautifulSoup(page, "html.parser")
    div = soup.find("ul", class_="question-index")
    links = div.find_all("a")

    for link in links:
        print(link["href"])
        get_question_links(baseurl + link["href"])


if __name__ == "__main__":
    main()