import requests
import json
import re
import time

def _build_headers(token=None):
    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-language": "en-GB,en-US;q=0.9,en;q=0.8",
        "content-type": "application/json",
        "origin": "https://app.carousel-learning.com",
        "priority": "u=1, i",
        "referer": "https://app.carousel-learning.com/",
        "sec-ch-ua": '"Google Chrome";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    }
    if token:
        headers["authorization"] = f"Bearer {token}"
    return headers
def get_quiz_id(link: str):
    pattern = r"[a-f0-9\-]{20,50}"
    match = re.search(pattern, link)
    if match:
        return match.group(0)
    return None
def get_group_id(quiz_id: str):
    url = f"https://api.carousel-learning.com/api/open/quizzes/{quiz_id}"
    try:
        response = requests.get(url, headers=_build_headers())
        response.raise_for_status()
        data = response.json()
        return data.get("data", {}).get("teachingGroup", {}).get("data", {}).get("id")
    except requests.RequestException as e:
        print(f"Error fetching group ID: {e}")
        return None
def get_token(quiz_id: str, forename: str, surname: str):
    group_id = get_group_id(quiz_id)
    if not group_id:
        return None
    url = "https://api.carousel-learning.com/api/auth/student/token"
    body = {
        "forename": forename,
        "surname": surname,
        "teachingGroupId": group_id,
    }
    try:
        response = requests.post(url, headers=_build_headers(), data=json.dumps(body))
        response.raise_for_status()
        data = response.json()
        return data.get("token")
    except requests.RequestException as e:
        print(e)
        return None
def get_quiz_attempt_data(quiz_id: str, token: str):
    url = f"https://api.carousel-learning.com/api/student/quizzes/{quiz_id}/attempts/last"
    try:
        response = requests.get(url, headers=_build_headers(token))
        response.raise_for_status()
        data = response.json().get("data", {})
        
        questions = data.get("quiz", {}).get("data", {}).get("questions", {}).get("data")
        attempt_id = data.get("id")

        if not questions or not attempt_id:
            print("Error: Could not find questions or attemptId in response.")
            return None, None
            
        questions_and_answers = [
            {"id": q["id"], "question": q["question"], "answer": q["perfectAnswer"]}
            for q in questions
        ]
        return questions_and_answers, attempt_id
    except requests.RequestException as e:
        print(e)
        return None, None
def start_answering(attempt_id: str, token: str):
    url = f"https://api.carousel-learning.com/api/student/attempts/{attempt_id}/state/answering"
    try:
        response = requests.post(url, headers=_build_headers(token), data=json.dumps({}))
        response.raise_for_status()
        return response.ok
    except requests.RequestException as e:
        print(f"Error starting answering state: {e}")
        return False
def submit_answer(attempt_id: str, question_id: str, answer: str, token: str):
    url = f"https://api.carousel-learning.com/api/student/attempts/{attempt_id}/answer"
    body = {"questionId": question_id, "answer": answer}
    try:
        response = requests.post(url, headers=_build_headers(token), data=json.dumps(body))
        response.raise_for_status()
        return response.ok
    except requests.RequestException as e:
        print(f"Error submitting answer for question {question_id}: {e}")
        return False
def mark_question(attempt_id: str, question_id: str, token: str):
    url = f"https://api.carousel-learning.com/api/student/attempts/{attempt_id}/marked/{question_id}"
    try:
        response = requests.post(url, headers=_build_headers(token), data=json.dumps({}))
        response.raise_for_status()
        return response.ok
    except requests.RequestException as e:
        print(f"Error marking question {question_id}: {e}")
        return False
def complete_attempt(attempt_id: str, token: str):
    url = f"https://api.carousel-learning.com/api/student/attempts/{attempt_id}/state/completed"
    try:
        response = requests.post(url, headers=_build_headers(token), data=json.dumps({}))
        response.raise_for_status()
        return response.ok
    except requests.RequestException as e:
        print(e)
        return False
def main():
    print("--- Carousel Autocompleter ---")
    forename = input("Enter your FORENAME: ").strip()
    surname = input("Enter your SURNAME: ").strip()
    link = input("Enter the full quiz LINK: ").strip()

    print("\n[1/8] Extracting Quiz ID...")
    quiz_id = get_quiz_id(link)
    if not quiz_id:
        print("Error: Could not find a valid ID in the link.")
        return
    print(f"Success. Quiz ID: {quiz_id}")

    print("\n[2/8] Getting authentication token...")
    token = get_token(quiz_id, forename, surname)
    if not token:
        print("Error: Failed to get token. Please check your details and the link.")
        return
    print("Success. Token received.")

    print("\n[3/8] Fetching quiz data and attempt ID...")
    questions_and_answers, attempt_id = get_quiz_attempt_data(quiz_id, token)
    if not attempt_id:
        print("Error: Failed to get quiz data.")
        return
    print(f"Success. Found {len(questions_and_answers)} questions for Attempt ID: {attempt_id}")

    print("\n[4/8] Setting quiz state to 'answering'...")
    if not start_answering(attempt_id, token):
        print("Error: Could not start the quiz.")
        return
    print("Success. Quiz started.")

    print("\n[5/8] Submitting answers...")
    total_questions = len(questions_and_answers)
    for i, qa in enumerate(questions_and_answers):
        submit_answer(attempt_id, qa['id'], qa['answer'], token)
        print(f"  > Submitted answer for question {i + 1}/{total_questions}")
        time.sleep(0.2)
    print("Success. All answers submitted.")
    
    print("\n[6/8] Marking questions as reviewed...")
    for i, qa in enumerate(questions_and_answers):
        mark_question(attempt_id, qa['id'], token)
        print(f"  > Marked question {i + 1}/{total_questions}")
        time.sleep(0.2)
    print("Success. All questions marked.")

    print("\n[7/8] Finalizing quiz completion...")
    if not complete_attempt(attempt_id, token):
        print("Warning: Could not finalize quiz, but answers were submitted.")
    else:
        print("Success. Quiz marked as completed.")
        
    print("\n[8/8] Generating results...")
    output_filename = f"answers-{quiz_id}.txt"
    with open(output_filename, "w", encoding="utf-8") as f:
        f.write(f"--- Answers for Carousel Quiz: {quiz_id} ---\n\n")
        for i, qa in enumerate(questions_and_answers):
            f.write(f"--- Question {i + 1} ---\n")
            f.write(f"Q: {qa['question']}\n")
            f.write(f"A: {qa['answer']}\n\n")
            
    print(f"\n--- ALL STEPS COMPLETE ---")
    print(f"The answers have been saved to the file: {output_filename}")


if __name__ == "__main__":
    main()
