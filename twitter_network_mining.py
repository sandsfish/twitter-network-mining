#!/usr/bin/env python

from twython import Twython
import json

# Application Credentials
APP_KEY = ''
APP_SECRET = ''

# OAuth Credentials for Personal Twitter Account
OAUTH_TOKEN = ''
OAUTH_TOKEN_SECRET = ''

twitter = Twython(APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)

# Output each tweet in given page of results
def print_tweets(results):
	for tweet in results['statuses']:
		print('-'+tweet['text'])

# Output all user mentions and hashtags for given page of results
def print_entities(page):
	for status in page['statuses']:
		user = twitter.show_user(user_id=status['user']['id'])
		print('= ' + user['screen_name'] + "(" + str(user['followers_count']) + " followers)")
	
		user_mentions = status['entities']['user_mentions']
		for mention in user_mentions:
			print('  Mentions: ' + mention['screen_name'])
	
		hash_tags = status['entities']['hashtags']
		for tag in hash_tags:
			print('  Tag: ' + tag['text'])

# Return list of hashtags used in the given page of results
def get_hashtags(page):
	tags = []
	for status in page['statuses']:
		tags.extend([tag['text'] for tag in status['entities']['hashtags']])
	return tags

# Return an array of all users who tweeted in the given page of results
def get_users(page):
	return [status['user']['id'] for status in page['statuses']]

# Return the max_id for the next results page 
def next_results(page):
	max_start = page['search_metadata']['next_results'].find('?max_id=')+8
	max_end = page['search_metadata']['next_results'].find('&q=')
	return page['search_metadata']['next_results'][max_start:max_end]

# Return boolean indicating if there is another page of results
def more_results(page):
	if('next_results' in page['search_metadata'].keys()):
		return True
	else:
		return False

# Return all hashtags used by users in given page, in their last 200 tweets
def get_first_hop_hashtags(page):
	one_hop_hashtags = []
	
	for u in get_users(page):
		timeline = twitter.get_user_timeline(user_id=u, count=200)
		for status in timeline:
			one_hop_hashtags.extend([tag['text'] for tag in status['entities']['hashtags']])
	
	# de-duplicate list and return
	return list(set(one_hop_hashtags))

# Collect all hashtags from first 200 statuses of each user that has tweeted about @username
query_term = '@username'
page_one = twitter.search(q=query_term, count=200, result_type='recent')

if(more_results(page_one)):
	page_two = twitter.search(max_id=next_results(page_one), q=query_term, count=200, result_type='recent')

hashtags = get_first_hop_hashtags(page_one)

# Output all discovered hashtags
for tag in hashtags:
	print('#' + tag + ', '),
