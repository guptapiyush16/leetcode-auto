import os
import requests
import time
from datetime import datetime
import smtplib
from email.message import EmailMessage

# Load environment variables
LEETCODE_SESSION = os.environ["LEETCODE_SESSION"]
CSRF_TOKEN = os.environ["CSRF_TOKEN"]
EMAIL_USER = os.environ["EMAIL_USER"]
EMAIL_PASS = os.environ["EMAIL_PASS"]
TO_EMAIL = os.environ["TO_EMAIL"]

# Submission schedule in UTC (11:30 PM IST = 18:00 UTC)
SCHEDULE_TIMES = [
    "2025-06-30 18:00:00",  # First submission
    "2025-07-01 18:00:00"   # Second submission
]

# LeetCode questions and their solutions
SUBMISSIONS = [
    {
        "slug": "two-sum",
        "language": "cpp",
        "code": """
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
    },
    {
        "slug": "valid-parentheses",
        "language": "cpp",
        "code": """
class Solution {
public:
    bool isValid(string s) {
        stack<char> st;
        for(char c : s){
            if(c == '(' || c == '[' || c == '{'){
                st.push(c);
            } else {
                if(st.empty()) return false;
                if(c == ')' && st.top() != '(') return false;
                if(c == ']' && st.top() != '[') return false;
                if(c == '}' && st.top() != '{') return false;
                st.pop();
            }
        }
        return st.empty();
    }
};
"""
    }
]

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
    headers = {
        "User-Agent": "Mozilla/5.0",
        "referer": f"https://leetcode.com/problems/{slug}/",
        "x-csrftoken": CSRF_TOKEN,
        "cookie": f"LEETCODE_SESSION={LEETCODE_SESSION}; csrftoken={CSRF_TOKEN}",
    }
    r = requests.post(url, json=query, headers=headers)
    return r.json()["data"]["question"]["questionId"]

def send_email(success, slug):
    msg = EmailMessage()
    msg['Subject'] = f"✅ LeetCode Auto Submission Status: {slug}"
    msg['From'] = EMAIL_USER
    msg['To'] = TO_EMAIL
    if success:
        msg.set_content(f"🎉 Your LeetCode problem '{slug}' was submitted successfully!")
    else:
        msg.set_content(f"❌ Submission failed for '{slug}'. Check your cookies or setup.")
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(EMAIL_USER, EMAIL_PASS)
        smtp.send_message(msg)

def submit_solution(slug, code, language):
    try:
        question_id = get_question_id(slug)
        headers = {
            "User-Agent": "Mozilla/5.0",
            "referer": f"https://leetcode.com/problems/{slug}/",
            "x-csrftoken": CSRF_TOKEN,
            "cookie": f"LEETCODE_SESSION={LEETCODE_SESSION}; csrftoken={CSRF_TOKEN}",
        }
        payload = {
            "lang": language,
            "question_id": str(question_id),
            "typed_code": code
        }
        res = requests.post(f"https://leetcode.com/problems/{slug}/submit/", json=payload, headers=headers)
        if res.status_code == 200:
            print(f"✅ Submission successful for: {slug}")
            send_email(True, slug)
        else:
            print(f"❌ Submission failed for: {slug}")
            send_email(False, slug)
    except Exception as e:
        print("🚨 Exception:", e)
        send_email(False, slug)

def wait_until(schedule_time_str):
    target_time = datetime.strptime(schedule_time_str, "%Y-%m-%d %H:%M:%S")
    while datetime.utcnow() < target_time:
        print("⏳ Waiting... UTC now:", datetime.utcnow())
        time.sleep(15)

def run_scheduler():
    for i in range(len(SCHEDULE_TIMES)):
        wait_until(SCHEDULE_TIMES[i])
        submit_solution(SUBMISSIONS[i]["slug"], SUBMISSIONS[i]["code"], SUBMISSIONS[i]["language"])

if __name__ == "__main__":
    run_scheduler()
