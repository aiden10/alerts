
import requests
from datetime import datetime
from zoneinfo import ZoneInfo 
import yaml
import json
import smtplib
import ssl
from email.message import EmailMessage
import os
from dotenv import dotenv_values

def time_ago(created_utc: float, tz: str = "America/New_York") -> str:
    local_time = datetime.fromtimestamp(created_utc, ZoneInfo(tz))
    now = datetime.now(ZoneInfo(tz))
    delta = now - local_time

    days = delta.days
    seconds = delta.seconds
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60

    if days > 0:
        return f"{days}d {hours}h ago"
    elif hours > 0:
        return f"{hours}h {minutes}m ago"
    elif minutes > 0:
        return f"{minutes}m ago"
    else:
        return "just now"

class Alerts:
    def __init__(self):
        self.target_subreddits = []
        self.keywords = []
        self.sender_email = ""
        self.recipient_email = ""
        self.sender_password = dotenv_values(".env")["PASSWORD"]

    def load_config(self):
        with open("config.yaml", "r", encoding="utf-8") as yaml_file:
            config = yaml.load(yaml_file, yaml.BaseLoader)
            self.sender_email = config["sender_email"]
            self.recipient_email = config["recipient_email"]
            self.target_subreddits = config["subreddits"]
            self.keywords = config["keywords"]
    
    def send_email(self, subject: str, body: str):
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
            em = EmailMessage()
            em['From'] = self.sender_email
            em['To'] = self.recipient_email
            em['Subject'] = subject
            em.set_content(body)
            
            smtp.login(self.sender_email, self.sender_password)
            
            try:
                smtp.sendmail(self.sender_email, self.recipient_email, em.as_string())
                print(f'email successfully sent to {self.recipient_email}')
            except Exception as e:
                print(f'Error sending email: {e}')
        
    def check_subreddits(self):
        for subreddit in self.target_subreddits:
            response = requests.get(f"https://www.reddit.com/r/{subreddit}/new.json")
            if response.status_code != 200:
                print(f"An error occurred: {response.text}")
                continue
            subreddit_data = json.loads(response.text)["data"]
            old_subreddit_data = []
            viewed_ids = []
            if os.path.isfile(f"{subreddit}.json"):
                old_subreddit_data = json.load(open(f"{subreddit}.json", "r", encoding="utf-8"))
            posts = subreddit_data["children"]
            for post in posts:
                id = post["data"]["id"]
                viewed_ids.append(id)
                if id in old_subreddit_data:
                    continue
                
                title = post["data"]["title"]
                selftext = post["data"]["selftext"]
                date = time_ago(post["data"]["created_utc"])
                link = f"https://www.reddit.com{post['data']['permalink']}"
                if any(keyword in title.lower() for keyword in self.keywords):
                    self.send_email(f"Post containing keyword found at r/{subreddit}", f"{title}\n{selftext}\n{link}\n\n{date}")
            
            with open(f"{subreddit}.json", "w", encoding="utf-8") as out_file:
                json.dump(viewed_ids, out_file)
                
if __name__ == "__main__":
    alerts = Alerts()
    alerts.load_config()
    alerts.check_subreddits()