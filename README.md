
# About
I made this because my mouse's scroll wheel is not working properly and I need a new one. 
I checked the r/bapcsalescanada subreddit for any mice deals and there happened to be a wireless mouse which normally goes for over $100 for only $15.
However, it went out of stock within a few hours and I was too late.
So I decided to create a simple scraper and setup a cron job on my server to run this every 5 minutes.

# Setup
To use this you'll have to setup an .env file in the same directory and install the dependencies.
```
PASSWORD=
CLIENT_ID=
CLIENT_SECRET=
USERNAME=
REDDIT_PASSWORD=
USER_AGENT=
```
The password is for the sender email address.

The client id and client secret are from the https://www.reddit.com/prefs/apps page. I made an app registered as a script because I kept getting blocked when trying to make direct GET requests to get posts.

The username and password are for your Reddit account.

Lastly, the user agent can just follow this format: platform:app_name:version (by /u/username)
