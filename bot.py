#!/usr/bin/python
import logging
import praw
import random
import time

#Imports all passwords from a hidden file ;)
from creds import *

SUBSCRIPTION_FILE = "subscribed_users.txt"
PROCESSED_MSG_IDS_FILE = "processed_message_ids.txt"
BOT_TAGGED_RESPONSES = [\
"You called? ;,", "What's up?", "Hey!", "Yo, 'sup?",
"Go check out my discord at https://github.com/TGWaffles/cryopodbot",
"Tagging me in a post can trigger specific things. " + \
"One of the random replies means I didn't understand what you asked!",
"Go check out Klok's patreon [here!](https://www.patreon.com/klokinator,",
"I was coded by /u/thomas1672 - direct all questions to him!",
"Now taking suggestions for more of these random supplies in the discord!",
"Join the discord @ https://discord.gg/EkdeJER"]

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




#Empty list to prevent double posts.
fixit = []
#For thread in the subreddit, out of the newest thread.
for submission in subreddit.get_new(limit=1):
	time.sleep(3)
	#Set variables to prevent annoying the reddit api.
	author = submission.author
	title = str(submission.title)
	id = str(submission.id)
	#Same as message checking but for threads.
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
		postedcomment = submission.add_comment("Hi. I'm a bot, bleep bloop." + "\n" + "\n" + "\n" + "\n" + "If you want to chat with 200+ fellow Cryopod readers, join the Discord at https://discord.gg/6JtsQJR" + "\n" + "\n" + "\n" + "[Click Here to be PM'd new updates!](https://np.reddit.com/message/compose/?to=CryopodBot&subject=Subscribe&message=Subscribe) " + "[Click Here to unsubscribe!](https://np.reddit.com/message/compose/?to=CryopodBot&subject=unsubscribe&message=unsubscribe)" + "\n" + "\n" + "\n" + "If you want to donate to Klokinator, send paypal gifts to Klokinator@yahoo.com, but be sure to mark it as a gift or Paypal takes 10%. " + "\n" + "\n" + "Patreon can also be pledged to [here!](https://www.patreon.com/klokinator)" + "\n" + "\n" + "This part consisted of: " + str(len(submission.selftext)) + " characters, " + str(len(str(submission.selftext).split())) + " words, and " + str(wc) + " unique words!" + "\n" + "\n" + "[" + "Previous Part" + "](" + prevurl + ")")
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
#Gets all comments in the subreddit, then flattens them.
subreddit_comments = subreddit.get_comments()
subcomments = praw.helpers.flatten_tree(subreddit_comments)
#Loops through every comment in the sub.
for comment in subcomments:
	#Opens file with comment ids.
	otherfile = open('done.txt','r+')
	#Do it twice to make sure.
	for i in range(2):
		for line in otherfile:
			linelen = len(line)
			newlinelen = linelen - 1
			if line[:newlinelen] not in already_done:
				already_done.append(line[:newlinelen])
	#If someone's tagging us and we've not processed their comment:
	if "/u/cryopodbot" in str(comment.body).lower() and str(comment.id) not in already_done:
		#If it's talking about the post, comment the post.
		if "post" in str(comment.body).lower():
			#Make sure the bot doesn't respond to itself.
			if str(comment.author).lower() != "cryopodbot":
				#Reply!
				comment.reply("Hi. I'm a bot, bleep bloop." + "\n" + "\n" + "If you're about to post regarding a typo and this Part was just posted, please wait ten minutes, refresh, and then see if it's still there!" + "\n" + "\n" + "Also, if you want to report typos anywhere, please respond to this bot to keep the main post clutter free. Thank you!" + "\n" + "\n" + "\n" + "[Click Here to be PM'd new updates!](https://np.reddit.com/message/compose/?to=CryopodBot&subject=Subscribe&message=Subscribe) " + "[Click Here to unsubscribe!](https://np.reddit.com/message/compose/?to=CryopodBot&subject=unsubscribe&message=unsubscribe)" + "\n" + "\n" + "\n" + "If you want to donate to Klokinator, send paypal gifts to Klokinator@yahoo.com, but be sure to mark it as a gift or Paypal takes 10%. " + "\n" + "\n" + "Patreon can also be pledged to [here!](https://www.patreon.com/klokinator)")
				#Post the ID to a file to prevent duplicates.
				otherfile.write(str(comment.id) + "\n")
		#If the post wants a flair and it's me or Klok:
		elif "flair info" in str(comment.body).lower():
			if str(comment.author).lower() == "thomas1672" or str(comment.author).lower() == "klokinator":
				flairsubmtoset = r.get_submission(submission_id=str(comment.parent_id)[-6:])
				#Flair and stop duplicate flairing (would only waste processor time)
				flairsubmtoset.set_flair("INFO", "info")
				otherfile.write(str(comment.id) + "\n")
		elif "flair question" in str(comment.body).lower():
			if str(comment.author).lower() == "thomas1672" or str(comment.author).lower() == "klokinator":
				flairsubmtoset = r.get_submission(submission_id=str(comment.parent_id)[-6:])
				flairsubmtoset.set_flair("QUESTION", "question")
				otherfile.write(str(comment.id) + "\n")
		elif str(comment.author).lower() != "cryopodbot":
                        response = random.choice(BOT_TAGGED_RESPONSES)
                        comment.reply(response)
			otherfile.write(str(comment.id) + "\n")
#Re-Save the file.
otherfile.close()


def set_up_reddit():
    user_agent = "Alternate cryopod implementation 1.0 by /u/robrys"
    reddit = praw.Reddit(user_agent = user_agent)
    reddit.login(REDDIT_USERNAME, REDDIT_PASS)
    return reddit

def unique_file_lines(file_name):
    unique_contents = set()
    file_handle = open(file_name, "r")
    for line in file_handle:
        unique_contents.add(line.strip())
    file_handle.close()
    return unique_contents

def is_unsubscribe_request(message):
    return "unsubscribe" in str(message.body).lower()

def is_subscribe_request(message):
    return "subscribe" in str(message.body).lower()

def is_subscribed(message.author, subscribed_users):
    return str(message.author) in subscribed_users

def is_processed_message_id(message_id, processed_message_ids):
    return str(message_id) in processed_message_ids

def overwrite_file(file_name, file_contents):
    file_handle = open(file_name, "w")
    file_handle.write(file_contents)
    file_handle.close()

def handle_subscription_messages(reddit):
    messages = reddit.get_messages()
    subscribed_users = unique_file_lines(SUBSCRIPTION_FILE)
    processed_message_ids = unique_file_lines(PROCESSED_MSG_IDS_FILE)

    for message in messages:
        print "Opening message!"
        if is_processed_message_id(message.id, processed_message_ids):
            continue

        # note: message ids that are neither subscribe/unsubscribe
        #       are not added to the processed message id file
        if is_unsubscribe_request(message) and
           is_subscribed(message.author, subscribed_users):
                subscribed_users.remove(str(message.author))
                processed_message_ids.add(str(message.id))
                message.reply("BOT: You've been unsubscribed!")

        elif is_subscribe_request(message) and
             not is_subscribed(message.author, subscribed_users):
                print "Adding someone! - " + str(message.author)
                subscribed_users.add(str(message.author))
                processed_message_ids.add(str(message.id))

    overwrite_file(SUBSCRIPTION_FILE, "\n".join(subscribed_users))
    overwrite_file(PROCESSED_MSG_IDS_FILE, "\n".join(processed_msg_ids))

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    reddit = set_up_reddit()

    handle_subscription_messages(reddit)



