import praw
import json
import smtplib
import ssl
from datetime import datetime
from zoneinfo import ZoneInfo
from email.message import EmailMessage
import os
import yaml
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

        creds = dotenv_values(".env")
        self.reddit = praw.Reddit(
            client_id=creds["CLIENT_ID"],
            client_secret=creds["CLIENT_SECRET"],
            username=creds["USERNAME"],
            password=creds["REDDIT_PASSWORD"],
            user_agent=creds["USER_AGENT"],
        )

    def load_config(self):
        with open("config.yaml", "r", encoding="utf-8") as yaml_file:
            config = yaml.safe_load(yaml_file)
            self.sender_email = config["sender_email"]
            self.recipient_email = config["recipient_email"]
            self.target_subreddits = config["subreddits"]
            self.keywords = config["keywords"]

    def send_email(self, subject: str, body: str):
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as smtp:
            em = EmailMessage()
            em["From"] = self.sender_email
            em["To"] = self.recipient_email
            em["Subject"] = subject
            em.set_content(body)

            smtp.login(self.sender_email, self.sender_password)

            try:
                smtp.sendmail(
                    self.sender_email, self.recipient_email, em.as_string()
                )
                print(f"email successfully sent to {self.recipient_email}")
            except Exception as e:
                print(f"Error sending email: {e}")

    def check_subreddits(self):
        for subreddit_name in self.target_subreddits:
            subreddit = self.reddit.subreddit(subreddit_name)

            old_ids = []
            if os.path.isfile(f"{subreddit_name}.json"):
                old_ids = json.load(
                    open(f"{subreddit_name}.json", "r", encoding="utf-8")
                )

            new_ids = []
            for submission in subreddit.new(limit=25):
                post_id = submission.id
                new_ids.append(post_id)

                if post_id in old_ids:
                    continue

                title = submission.title
                selftext = submission.selftext
                date = time_ago(submission.created_utc)
                link = f"https://www.reddit.com{submission.permalink}"

                if any(k.lower() in title.lower() for k in self.keywords):
                    self.send_email(
                        f"Post containing keyword found at r/{subreddit_name}",
                        f"{title}\n{selftext}\n{link}\n\n{date}",
                    )

            with open(f"{subreddit_name}.json", "w", encoding="utf-8") as out_file:
                json.dump(new_ids, out_file)


if __name__ == "__main__":
    alerts = Alerts()
    alerts.load_config()
    alerts.check_subreddits()