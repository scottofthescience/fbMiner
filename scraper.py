'''
	This python module is used for data mining via the facebook-sdk python module
	for the Cornell University Social Media Lab and Northwestern University Social
	Media Lab
'''

import facebook
import json
from time import sleep
import urllib2
import datetime

global ACCESS_TOKEN
global confession_id
confession_id = '618332588183265'
global APP_ID
APP_ID = "463500207102372"
global APP_SECRET
APP_SECRET = "863524a429198f237fc09d3dbb2f5c04"
global long_token
long_token = 'CAAGljQ0ymaQBABg3l9iimZAG23lEX3g5ackfEmYaj7LzEPN5j5nVx8KPguNjlY77uFTR9GfGHtlLAZBEtYWQNIYzCfemFMc3Y5ftZBgANVTVoZBKrmH4xOF9ktPF4Q3imZByw2jj5y8wZBaeZBi9qFdxtMeZAMKeRY6oqpYgWD5CttSZBz1ENKZCVHBMDfraBbszMZD'
def set_token(string):
	ACCESS_TOKEN = string

def get_data(token):
	ACCESS_TOKEN = token
	num_pages = 1
	posts = []
	g = facebook.GraphAPI(ACCESS_TOKEN)
	# get initial page
	page1 = g.get_connections(confession_id, "feed", limit=1000)
	posts += page1['data']
	nextString = page1['paging']['next']
	next = nextString.split("until=")[-1]
	while True:
		print "page : " + str(num_pages)
		time.sleep(1)
		page = g.get_connections(confession_id, "feed", limit=1000, until=next)
		if 'data' in page.keys():
			posts += page['data']
			num_pages+=1
		else:
			break
		if 'paging' in page.keys():
			if 'next' in page['paging']:
				nextString = page['paging']['next']
				next = nextString.split("until=")[-1]
			else:
				break
		else:
			break
	return posts

def getLikes(post_id, g, wait=0):
	num_likes = 0
	like_obj = g.get_connections(post_id, "likes", limit=1000)
	num_likes = len(like_obj['data'])
	if wait > 0:
		sleep(wait)
	return num_likes

def getLikeData(posts, token):
	num_likes_arr = []
	like_posters = []
	g = facebook.GraphAPI(token)
	count = 1
	for p in posts:
		print "post #" + str(count)
		count += 1
		post_id = p['id']
		if 'likes' in p.keys():
			while True:
				try:
					num_likes = getLikes(post_id, g)
				except facebook.GraphAPIError as gep:
					print gep
					token = raw_input("enter new token : " )
					g = facebook.GraphAPI(token)
				except urllib2.URLError as urlerr:
					print urlerr
					print "waiting 10 minutes at :"
					print datetime.datetime.now()
					sleep(1800)
					g = facebook.GraphAPI(token)
				except ValueError as ve:
					print ve
					sleep(180)
				else:
					break
			num_likes_arr.append(num_likes)
		else:
			num_likes_arr.append(0)
	return num_likes_arr

def getComments(post_id, g, wait=0):
	''' for a post_id, look up all comments and get the comment_id, user_name, user_id, time, num_likes, and message '''
	comments = []
	comm_obj = g.get_connections(post_id, "comments", limit=1000)
	for comm in comm_obj['data']:
		comment = [post_id, comm['id'],
				comm['from']['name'],
				comm['from']['id'],
				comm['created_time'],
				comm['like_count'],
				comm['message']]
		comments.append(comment)
	if wait > 0:
		sleep(wait)
	return comments

def getCommentData(posts, token):
	comments = []
	g = facebook.GraphAPI(token)
	count = 1
	for p in posts:
		print "Post #" + str(count)
		count += 1
		if 'comments' in p.keys():
			while True:
				try:
					comms = getComments(post_id, g)
				except facebook.GraphAPIError as gep:
					print gep
					token = raw_input("enter new token : " )
					g = facebook.GraphAPI(token)
				except urllib2.URLError as urlerr:
					print urlerr
					print "waiting 10 minutes at :"
					print datetime.datetime.now()
					sleep(1800)
					g = facebook.GraphAPI(token)
				else:
					break
			for comm in comms:
				comments.append(comm)
	return comments

def getArr(token, posts=0):
	g = facebook.GraphAPI(token)
	if posts == 0:
		posts = get_data(token)
	post_rows = [['post_id', 'time', 'message', 'num_likes', 'num_comments', 'type']]
	comment_rows = [['post_id', 'comment_id', 'user_name', 'user_id', 'time', 'like_count', 'message']]
	count = 1
	num = len(posts)
	for p in posts:
		print "Post #" + str(count) + " out of " + str(num)
		count +=1
		likes = 0
		num_comms = 0
		message =''
		if 'message' in p.keys():
			message = p['message']
		if 'likes' in p.keys():
			while True:
				try:
					likes = getLikes(p['id'], g)
				except facebook.GraphAPIError as gep:
					print gep
					token = raw_input("enter new token : " )
					g = facebook.GraphAPI(token)
				except urllib2.URLError as urlerr:
					print urlerr
					print "waiting 10 minutes at :"
					print datetime.datetime.now()
					sleep(1800)
					g = facebook.GraphAPI(token)
				else:
					break

		if 'comments' in p.keys():
			while True:
				try:
					comments = getComments(p['id'], g)
				except facebook.GraphAPIError as gep:
					print gep
					token = raw_input("enter new token : " )
					g = facebook.GraphAPI(token)
				except urllib2.URLError as urlerr:
					print urlerr
					print "waiting 10 minutes at :"
					print datetime.datetime.now()
					sleep(1800)
					g = facebook.GraphAPI(token)
				else:
					break
			num_comms = len(comments)
			for c in comments:
				comment_rows.append(c)

		post_row = [p['id'],
					p['created_time'],
					message,
					likes,
					num_comms,
					p['type']]
		post_rows.append(post_row)
	return post_rows, comment_rows

def arr_to_string(arr):
	new_rows = []
	for p in arr:
		new_row = []
		for x in p:
			val = x
			stringVal = ''
			try:
				if type(x) is type(u''):
					stringVal = val.encode('ascii', 'ignore').replace('\n', ' ')
				else:
					stringVal = str(x).encode('ascii','ignore')
			except UnicodeEncodeError as uee:
				print uee
				print x
				raw_input('press any key')
			new_row.append(stringVal)
		new_rows.append(new_row)
	return new_rows

