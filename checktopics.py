import re
import base64
import glob, json

from bs4 import BeautifulSoup
import requests

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
    baseurl = "https://www.bomcondutor.pt/questao/"

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


for file in glob.glob("topicos/*.json"):
    with open(file, "r") as f:
        data = json.load(f)
        modified = False
        
        for a in data:
            count = len(a["answers"])
            correct = 0
            wrong = 0
            
            for i, el in enumerate(a["answers"]):
                if el["correct"] == True:
                    correct += 1
                else:
                    wrong += 1
                    
            if correct == 0:
                modified = True
            elif wrong == 0:
                modified = True

        if modified:
            with open(file, "w") as f:
                json.dump(data, f, indent=2)
                print(f"Modified {file}")