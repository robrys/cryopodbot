import praw
import pprint
import time

user_agent = "Super basic bot usage by /u/robrys"
reddit = praw.Reddit(user_agent=user_agent, site_name = "demo_bot")

while True:
    subreddit = reddit.get_subreddit('thecryopodtohell')
    for submission in subreddit.get_hot(limit=10):
        pprint.pprint(submission.title)
    time.sleep(5)



"""
Interesting fields of submission object

'author'
'comments'
'id'
'name'
'selftext'
'subreddit'
'subreddit_id'
'title'
"""
