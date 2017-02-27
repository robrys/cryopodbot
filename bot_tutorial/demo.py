import praw
import pprint
import time
import logging

# Imports REDDIT_USERNAME and REDDIT_PASSWORD
from creds import *

logging.basicConfig(level=logging.INFO)
user_agent = "Alternate cryopod implementation 1.0 by /u/robrys"
reddit = praw.Reddit(user_agent=user_agent)

reddit.login(REDDIT_USERNAME, REDDIT_PASSWORD, disable_warning=True)
#for message in reddit.get_messages():
    #print message.body
    #pprint.pprint(vars(message))

subreddit = reddit.get_subreddit("thecryopodtohell")
for submission in subreddit.get_new(limit = 1):
       author = submission.author
       print author
       time.sleep(0)
       if str(author).lower() == "klokinator":
               print submission.title
               time.sleep(0)
               #if str(submission.title)[0:4].lower() == "part"

