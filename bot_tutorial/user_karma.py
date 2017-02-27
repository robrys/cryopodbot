import praw
import pprint

user_agent = "Karma breakdown 1.0 by /u/robrys"
reddit = praw.Reddit(user_agent=user_agent)

user_name = "rahhbertt"
user = reddit.get_redditor(user_name)

karma_by_subreddit = {}
thing_limit = 10
submitted_generator = user.get_submitted(limit=thing_limit)

for thing in submitted_generator:
    subreddit = thing.subreddit.display_name
    karma_by_subreddit[subreddit] = (karma_by_subreddit.get(subreddit, 0)
                                     + thing.score)

pprint.pprint(karma_by_subreddit)





