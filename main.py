import os
import requests
import time
from datetime import datetime
import smtplib
from email.message import EmailMessage

# Fetch LeetCode cookie values from environment
LEETCODE_SESSION = os.environ["LEETCODE_SESSION"]
CSRF_TOKEN = os.environ["CSRF_TOKEN"]
EMAIL_USER = os.environ["EMAIL_USER"]
EMAIL_PASS = os.environ["EMAIL_PASS"]
TO_EMAIL = os.environ["TO_EMAIL"]

SCHEDULE_TIME = "2025-06-29 18:30:00"
QUESTION_TITLE_SLUG = "two-sum"
LANGUAGE = "cpp"

CODE = """
class Solution {
public:
    vector<int> twoSum(vector<int>& nums, int target) {
        unordered_map<int, int> mp;
        for(int i = 0; i < nums.size(); i++) {
            int diff = target - nums[i];
            if(mp.find(diff) != mp.end())
                return {mp[diff], i};
            mp[nums[i]] = i;
        }
        return {};
    }
};
"""

headers = {
    "User-Agent": "Mozilla/5.0",
    "referer": f"https://leetcode.com/problems/{QUESTION_TITLE_SLUG}/",
    "x-csrftoken": CSRF_TOKEN,
    "cookie": f"LEETCODE_SESSION={LEETCODE_SESSION}; csrftoken={CSRF_TOKEN}",
}

def get_question_id(slug):
    url = "https://leetcode.com/graphql"
    query = {
        "query": """
        query getQuestionDetail($titleSlug: String!) {
          question(titleSlug: $titleSlug) {
            questionId
          }
        }
        """,
        "variables": {"titleSlug": slug}
    }
    r = requests.post(url, json=query, headers=headers)
    return r.json()["data"]["question"]["questionId"]

def send_email(success):
    msg = EmailMessage()
    msg['Subject'] = '✅ LeetCode Auto Submission Status'
    msg['From'] = EMAIL_USER
    msg['To'] = TO_EMAIL
    if success:
        msg.set_content("🎉 Your LeetCode problem was submitted successfully!")
    else:
        msg.set_content("❌ Submission failed. Check your cookies or setup.")
    
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(EMAIL_USER, EMAIL_PASS)
        smtp.send_message(msg)

def submit_solution():
    try:
        question_id = get_question_id(QUESTION_TITLE_SLUG)
        submit_url = f"https://leetcode.com/problems/{QUESTION_TITLE_SLUG}/submit/"
        payload = {
            "lang": LANGUAGE,
            "question_id": str(question_id),
            "typed_code": CODE
        }

        res = requests.post(submit_url, json=payload, headers=headers)
        if res.status_code == 200:
            print("✅ Submission successful!")
            send_email(True)
        else:
            print("❌ Submission failed!")
            print(res.text)
            send_email(False)
    except Exception as e:
        print("🚨 Exception:", e)
        send_email(False)

def wait_until(schedule_str):
    submit_time = datetime.strptime(schedule_str, "%Y-%m-%d %H:%M:%S")
    while datetime.utcnow() < submit_time:
        print("⏳ Waiting... now:", datetime.utcnow())
        time.sleep(10)
    submit_solution()

wait_until(SCHEDULE_TIME)
