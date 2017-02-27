#!/usr/bin/python
import logging
import praw
import random
import time

from creds import *

BOT_USERNAME = "cryopodbot"
TOM_USERNAME = "thomas1672"
KLOK_USERNAME = "klokinator"
SUBSCRIPTION_FILE = "subscribed_users.txt"
PROCESSED_MSG_IDS_FILE = "processed_message_ids.txt"

MESSAGE_BOT_LINK = "https://np.reddit.com/message/compose/?to=CryopodBot"
SUBSCRIBE_LINK = MESSAGE_BOT_LINK + "&subject=Subscribe&message=Subscribe"
UNSUBSCRIBE_LINK = MESSAGE_BOT_LINK + "&subject=unsubscribe&message=unsubscribe"
PAYPAL_EMAIL = "Klokinator@yahoo.com"
PATREON_LINK = "https://www.patreon.com/klokinator"
FOOTER_MESSAGE = """\
[Click Here to be PM'd new updates!] (%(sub_link)s)\
[Click Here to unsubscribe!] (%(unsub_link)s)\n\n\n\
If you want to donate to Klokinator, send paypal gifts to %(paypal_email)s, \
but be sure to mark it as a gift or Paypal takes 10%%.\n\n\
Patreon can also be pledged to [here!] (%(patreon_link)s)\n\n\
""" % dict(sub_link=SUBSCRIBE_LINK, unsub_link=UNSUBSCRIBE_LINK,
           paypal_email=PAYPAL_EMAIL, patreon_link=PATREON_LINK)

BOT_POST_COMMENT_RESPONSE = """\
Hi. I'm a bot, bleep bloop.\n\n\
If you're about to post regarding a typo and this Part was just posted, \
please wait ten minutes, refresh, and then see if it's still there!\n\n\
Also, if you want to report typos anywhere, please respond to this bot to \
keep the main post clutter free. Thank you!\n\n\n\
""" + FOOTER_MESSAGE

BOT_TAGGED_RESPONSES = [\
    "You called? ;,", "What's up?", "Hey!", "Yo, 'sup?",
    "Go check out my discord at https://github.com/TGWaffles/cryopodbot",
    "Tagging me in a post can trigger specific things. " + \
    "One of the random replies means I didn't understand what you asked!",
    "Go check out Klok's patreon [here!] (" + PATREON_LINK + ")",
    "I was coded by /u/thomas1672 - direct all questions to him!",
    "Now taking suggestions for more of these random supplies in the discord!",
    "Join the discord @ https://discord.gg/EkdeJER"]

BOT_FIRST_COMMENT_RESPONSE = """\
Hi. I'm a bot, bleep bloop.\n\n\n\n\
If you want to chat with 200+ fellow Cryopod readers, \
join the Discord at https://discord.gg/6JtsQJR\n\n\n""" + FOOTER_MESSAGE + \
"""\
This part consisted of: %(char_count)s" characters, %(word_count)s words, and \
%(unique_word_count)s unique words!\n\n\
[Previous Part] (%(prev_url)s)"""

#Fetches all messages sent to the bot.
def removel(who):
	f = open("list.txt","r+")
	d = f.readlines()
	f.seek(0)
	for i in d:
		if str(who) != i:
			f.write(i)
	f.truncate()
	f.close()

def set_up_reddit():
    user_agent = "Alternate cryopod implementation 1.0 by /u/robrys"
    reddit = praw.Reddit(user_agent = user_agent)
    reddit.login(REDDIT_USERNAME, REDDIT_PASSWORD, disable_warning=True)
    return reddit

def unique_file_lines(file_name):
    unique_contents = set()
    file_handle = open(file_name, "r")
    for line in file_handle:
        unique_contents.add(line.strip())
    file_handle.close()
    return unique_contents

def is_unsubscribe_request(message):
    return "unsubscribe" in unicode(message.body).lower()

def is_subscribe_request(message):
    return "subscribe" in unicode(message.body).lower()

def is_subscribed(message_author, subscribed_users):
    return unicode(message_author).lower().strip() in subscribed_users

def is_processed_message_id(message_id, processed_message_ids):
    return unicode(message_id).strip() in processed_message_ids

def overwrite_file(file_name, file_contents):
    file_handle = open(file_name, "w")
    file_handle.write(file_contents)
    file_handle.close()

def process_subscription_messages(reddit):
    messages = reddit.get_messages()
    subscribed_users = unique_file_lines(SUBSCRIPTION_FILE)
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
                message.reply("BOT: You've been unsubscribed!")

        elif is_subscribe_request(message) and \
             not is_subscribed(message.author, subscribed_users):
                print "Adding someone! - " + unicode(message.author)
                subscribed_users.add(unicode(message.author))
                processed_message_ids.add(unicode(message.id))

    overwrite_file(SUBSCRIPTION_FILE, "\n".join(subscribed_users))
    overwrite_file(PROCESSED_MSG_IDS_FILE, "\n".join(processed_message_ids))

def is_bot_tagged(comment):
    return "/u/cryopodbot" in unicode(comment.body).lower().strip()

def is_post_about(keyword, comment):
    return keyword in unicode(comment.body).lower()

def is_author(username, comment):
    return unicode(comment.author).lower() == username

def process_tagged_comments(reddit):
    subreddit = reddit.get_subreddit("thecryopodtohell")
    subreddit_comments = subreddit.get_comments()
    subcomments = praw.helpers.flatten_tree(subreddit_comments)
    processed_message_ids = unique_file_lines(PROCESSED_MSG_IDS_FILE)

    # Loops through every comment in the sub.
    for comment in subcomments:
        if is_bot_tagged(comment) and \
           not is_author(BOT_USERNAME, comment) and \
           not is_processed_message_id(comment.id, processed_message_ids):

                # If it's talking about the post, comment the post.
                if is_post_about("post", comment):
                    comment.reply(BOT_POST_COMMENT_RESPONSE)
                    processed_message_ids.add(unicode(comment.id))

                #If the post wants a flair and it's me or Klok:
                elif is_post_about("flair info", comment) and \
                     (is_author(TOM_USERNAME, comment) or \
                      is_author(KLOK_USERNAME, comment)):
                        #Flair and stop duplicate flairing (would only waste processor time)
                        flairsubmtoset = reddit.get_submission(submission_id=unicode(comment.parent_id)[-6:])
                        flairsubmtoset.set_flair("INFO", "info")
                        processed_message_ids.add(unicode(comment.id))

                elif is_post_about("flair question", comment) and \
                     (is_author(TOM_USERNAME, comment) or \
                      is_author(KLOK_USERNAME, comment)):
                        flairsubmtoset = reddit.get_submission(submission_id=unicode(comment.parent_id)[-6:])
                        flairsubmtoset.set_flair("QUESTION", "question")
                        processed_message_ids.add(unicode(comment.id))

                # Every other comment tagging the bot, just say some message
                else:
                    response = random.choice(BOT_TAGGED_RESPONSES)
                    comment.reply(response)
                    processed_message_ids.add(unicode(comment.id))

    overwrite_file(PROCESSED_MSG_IDS_FILE, "\n".join(processed_message_ids))

def process_submissions(reddit):
    subreddit = reddit.get_subreddit("thecryopodtohell")
    #Empty list to prevent double posts.
    fixit = []
    #For thread in the subreddit, out of the newest thread.
    for submission in subreddit.get_new(limit=1):
        time.sleep(3)
        #Set variables to prevent annoying the reddit api.
        author = submission.author
        title = unicode(submission.title)
        id = unicode(submission.id)
        #Same as message checking but for threads.
        fixit = unique_file_lines(PARTS_FILE)

        file = open('parts.txt','r+')
        for line in file:
            linelen = len(line)
            newlinelen = linelen - 1
            if line[:newlinelen] not in fixit:
                fixit.append(line[:newlinelen])

        #If the author is Klok and it begins with part, do this:
        if str(author).lower() == "klokinator" and title[0:4].lower() == "part" and id not in fixit or str(author).lower() == "thomas1672" and title[0:4].lower() == "test" and id not in fixit:
            file.write(id + "\n")
            file.close()
            file = open('lastpart.txt', 'r')
            lastprt = file.readline()
            file.close()
            alreadyin = []
            finished = []
            todo = []
            nxtparts = r.get_submission(lastprt)
            nxtpart = nxtparts.comments[0]
            add = nxtpart.body + "\n" + "\n" + "**[" + submission.title + "](" + submission.permalink + ")**"
            nxtpart.edit(add)
            prev = r.get_info(thing_id=nxtpart.parent_id)
            prevurl = prev.permalink
            uwc = []
            wc = 0
            for i in str(submission.selftext).split():
                if i not in uwc:
                    wc += 1
                    uwc.append(i)
            #Post the comment on the thread.
            postedcomment = submission.add_comment(BOT_FIRST_COMMENT_RESPONSE)
            file = open('lastpart.txt', 'w')
            file.write(str(postedcomment.permalink))
            file.close()
            file = open('list.txt', 'r+')
            submission.set_flair("STORY", "story")
            #Sticky the comment that was just posted.
            postedcomment.distinguish(sticky=True)
            #Get the index list's ID.
            toedit = r.get_submission(submission_id='56tvbw')
            time.sleep(2)
            #Add post that was just posted to the index list.
            tempedit = toedit.selftext
            putin = tempedit + "\n" + "\n" + "[" + submission.title + "](" + submission.permalink + ")"
            time.sleep(2)
            toedit.edit(putin)
            time.sleep(2)
            if title[0:4].lower() != "test":
                #Put all users in the username file into a list, then:
                for line in file:
                    linelen = len(line)
                    newlinelen = linelen -1
                    if line[:newlinelen] not in alreadyin:
                        alreadyin.append(line[:newlinelen])
                #For every name in the list, send them this message with the link to the part.
                for name in alreadyin:
                    try:
                        r.send_message(name, "New Post!", "New Post on /r/TheCryopodToHell! - [" + title + "](" + submission.permalink + ")")
                        finished.append(str(name))
                    except Exception as ex:
                        print(ex)
                        print(name)
                        f = open('offenders.txt','r+')
                        f.write(name + "\n")
                        f.close()
                    time.sleep(1)
                time.sleep(10)
                for line in file:
                    linelen = len(line)
                    newlinelen = linelen -1
                    if line[:newlinelen] not in finished:
                        todo.append(line[:newlinelen])
                for name in todo:
                    try:
                        r.send_message(name, "New Post!", "New Post on /r/TheCryopodToHell! - [" + title + "](" + submission.permalink + ")")
                    except Exception as ex:
                        print(ex)
                        print(name)
                        f = open('offenders.txt','r+')
                        f.write(name + "\n")
                        f.close()
                        torem = name + "\n"
                        removel(torem)
                    time.sleep(1)
                file.close()

    else:
        file.close()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    reddit = set_up_reddit()

    process_subscription_messages(reddit)
    process_tagged_comments(reddit)
    #process_submissions(reddit)

