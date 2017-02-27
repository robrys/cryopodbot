#!/usr/bin/python
import logging
import praw
import random
import time

from creds import *
from common_util import *

def set_up_reddit():
    user_agent = "Alternate cryopod implementation 1.0 by /u/robrys"
    reddit = praw.Reddit(user_agent = user_agent)
    reddit.login(REDDIT_USERNAME, REDDIT_PASSWORD, disable_warning=True)
    return reddit

def process_subscription_messages(reddit):
    messages = reddit.get_messages()
    subscribed_users = unique_file_lines(SUBSCRIBED_USERS_FILE)
    processed_message_ids = unique_file_lines(PROCESSED_MSG_IDS_FILE)

    for message in messages:
        print "Opening message!"
        if is_processed_message_id(message.id, processed_message_ids):
            continue

        # note: message ids that are neither subscribe/unsubscribe
        #       are not added to the processed message id file
        if is_unsubscribe_request(message) and \
           is_subscribed(message.author, subscribed_users):
                subscribed_users.remove(unicode(message.author))
                processed_message_ids.add(unicode(message.id))
                print unicode(message.id)
                print "unsubscribed reply sent"
                #message.reply("BOT: You've been unsubscribed!")

        elif is_subscribe_request(message) and \
             not is_subscribed(message.author, subscribed_users):
                print "Adding someone! - " + unicode(message.author)
                subscribed_users.add(unicode(message.author))
                print unicode(message.id)
                processed_message_ids.add(unicode(message.id))

    overwrite_file(SUBSCRIBED_USERS_FILE, "\n".join(subscribed_users))
    overwrite_file(PROCESSED_MSG_IDS_FILE, "\n".join(processed_message_ids))

# Only gets the first page of r/TheCryopodToHell/comments
# presumably this gets run often enough that this is okay
def process_tagged_comments(reddit):
    subreddit = reddit.get_subreddit("thecryopodtohell")

    subreddit_comments = subreddit.get_comments()
    subcomments = praw.helpers.flatten_tree(subreddit_comments)
    processed_message_ids = unique_file_lines(PROCESSED_MSG_IDS_FILE)

    for comment in subcomments:
        print "comment:\n\t\t%s\n\n***\n\n" % comment.body
        if is_bot_tagged(comment) and \
           not is_author(BOT_USERNAME, comment) and \
           not is_processed_message_id(comment.id, processed_message_ids):

                # If it's talking about the post, comment the post.
                if is_post_about("post", comment):
                    print unicode(comment.id)
                    print BOST_POST_COMMENT_RESPONSE
                    #comment.reply(BOT_POST_COMMENT_RESPONSE)
                    processed_message_ids.add(unicode(comment.id))

                #If the post wants a flair and it's me or Klok:
                elif is_post_about("flair info", comment) and \
                     (is_author(TOM_USERNAME, comment) or \
                      is_author(KLOK_USERNAME, comment)):
                        #Flair and stop duplicate flairing (would only waste processor time)

                        flairsubmtoset = reddit.get_submission(submission_id=unicode(comment.parent_id)[-6:])
                        print unicode(comment.id)
                        print "flair info"
                        #flairsubmtoset.set_flair("INFO", "info")
                        processed_message_ids.add(unicode(comment.id))

                elif is_post_about("flair question", comment) and \
                     (is_author(TOM_USERNAME, comment) or \
                      is_author(KLOK_USERNAME, comment)):
                        flairsubmtoset = reddit.get_submission(submission_id=unicode(comment.parent_id)[-6:])
                        print unicode(comment.id)
                        print "flair question"
                        #flairsubmtoset.set_flair("QUESTION", "question")
                        processed_message_ids.add(unicode(comment.id))

                # Every other comment tagging the bot, just say some message
                else:
                    response = random.choice(BOT_TAGGED_RESPONSES)
                    print unicode(comment.id)
                    print response
                    #comment.reply(response)
                    processed_message_ids.add(unicode(comment.id))

    # note: should probably overwrite_file() after every concrete action
    #       like .reply() or.set_flair()
    overwrite_file(PROCESSED_MSG_IDS_FILE, "\n".join(processed_message_ids))

def post_bot_first_comment(submission):
    bot_comment = format_bot_first_comment(submission)
    posted_bot_comment = submission.add_comment(bot_first_comment)
    posted_bot_comment.distinguish(sticky=True)
    submission.set_flair("STORY", "story")
    return posted_bot_comment

def process_submissions(reddit):
    subreddit = reddit.get_subreddit("thecryopodtohell")
    #For thread in the subreddit, out of the newest thread.
    for submission in subreddit.get_new(limit=1):
        time.sleep(3)
        #Set variables to prevent annoying the reddit api.
        # does every access of a .field hit the api?
        # i thought lazy objects means only the first access does
        # since those fields are immutable???

        # Same as message checking but for threads.
        # Empty list to prevent double posts.
        webseries_parts = unique_file_lines(ALL_WEBSERIES_PARTS_FILE)

        #If the author is Klok and it begins with part, do this:
        if (is_author(KLOK_USERNAME, submission) and \
            is_webseries_part(submission) and \
            not is_processed_webseries_part(submission.id, webseries_parts)) or \
           (is_author(TOM_USERNAME, submission) and \
            is_test_webseries_part(submission) and \
            not is_processed_webseries_part(submission.id, webseries_parts)):
                # move this after all work is done? in case fails
                webseries_parts.add(unicode(submission.id))
                overwrite_file(ALL_WEBSERIES_PARTS_FILE, "\n".join(webseries_parts))

                link_previous_part_to_latest(submission)

                #Post the comment on the thread.
                posted_bot_comment = post_bot_first_comment(submission)

                newest_webseries_part_url = unicode(posted_bot_comment.permalink)
                overwrite_file(LATEST_WEBSERIES_PART_FILE, newest_webseries_part_url)

                link_index_list_to_latest(submission)

# lastpart.txt is actually a link to the bot's stickied comment!!
# need to update docs

                if not is_test_webseries_part(submission):
                    notify_subscribed_users(submission)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    reddit = set_up_reddit()

    process_subscription_messages(reddit)
    process_tagged_comments(reddit)
    #process_submissions(reddit)

