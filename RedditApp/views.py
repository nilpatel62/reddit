from django.http import JsonResponse
from rest_framework.views import APIView
from bs4 import BeautifulSoup
import requests
import requests.auth
from imgurpython import ImgurClient
import urllib
import os
import pandas as pd
from django.shortcuts import render, redirect
import json
from pymongo import MongoClient
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import datetime
import praw
from dateutil.relativedelta import relativedelta
from bson.objectid import ObjectId


client = MongoClient("mongodb://root_DB:hmZaetjjj2Njqa2V@3.220.52.253:27017/reddit")
db = client["reddit"]

base_url = "http://127.0.0.1:8000" # for the localhost
# base_url = "http://redditscrape.solvingresidentburnout.com" # for the live


# image_path = "/opt/Reddit/Reddit/RedditApp/images"
image_path = "/home/embed/RedditApp/Reddit/RedditApp/images"

# email address details

# li = ["daniel@solvingresidentburnout.com"]
li = ["nilpatel62@gmail.com"]
name = ["daniel"]
sender_email = "solvingresidentburnout@gmail.com"
password = "4jN^Dj7Z4dA"

url = "https://www.reddit.com/r/"
# all credential or connection for imgur
client_id = '95eb3736be8e9a5'
client_secret = '3d46054a66c1f606c8fb1b8f9eeb52630807b2bc'
access_token = '389ab6133ea99b2d0f4632e101a391501122d66e'
refresh_token = '6ef0238aa4f7984a95d40ea3150e537ab92dac07'
client = ImgurClient(client_id, client_secret, access_token, refresh_token)
album = "0BBCRqh" # You can also enter an album ID here
final_list = []

headers = {
	'User-Agent': "PostmanRuntime/7.14.0",
	'Accept': "*/*",
	'Cache-Control': "no-cache",
	'Host': "www.reddit.com",
	'cache-control': "no-cache"
}


def upload_image(client, image_upload):
	for i in image_upload:
		config = {
			"Authorization": "Client-ID aca2fccc6890640",
			'album': album,
			'name': i['text'],
			'title': i['text'],
			'description': i['text']
		}
		print("Uploading image... ")
		uploaded_image = client.upload_from_path(i['image'], config=config, anon=False)
		print("Done")
	return uploaded_image


def get_past_date(str_days_ago):
    TODAY = datetime.date.today()
    splitted = str_days_ago.split()
    if len(splitted) == 1 and splitted[0].lower() == 'today':
        return str(TODAY.isoformat())
    elif len(splitted) == 1 and splitted[0].lower() == 'yesterday':
        date = TODAY - relativedelta(days=1)
        return str(date.isoformat())
    elif splitted[1].lower() in ['hour', 'hours', 'hr', 'hrs', 'h']:
        date = datetime.datetime.now() - relativedelta(hours=int(splitted[0]))
        return str(date.date().isoformat())
    elif splitted[1].lower() in ['day', 'days', 'd']:
        date = TODAY - relativedelta(days=int(splitted[0]))
        return str(date.isoformat())
    elif splitted[1].lower() in ['wk', 'wks', 'week', 'weeks', 'w']:
        date = TODAY - relativedelta(weeks=int(splitted[0]))
        return str(date.isoformat())
    elif splitted[1].lower() in ['mon', 'mons', 'month', 'months', 'm']:
        date = TODAY - relativedelta(months=int(splitted[0]))
        return str(date.isoformat())
    elif splitted[1].lower() in ['yrs', 'yr', 'years', 'year', 'y']:
        date = TODAY - relativedelta(years=int(splitted[0]))
        return str(date.isoformat())
    else:
        return "Wrong Argument format"


def my_reddit_search():
	reddit_data = db.reddit.find({})
	print("====", reddit_data.count())
	for i in reddit_data:
		try:
			print(i)
			url = "https://www.reddit.com/r/"
			search_url = i['url']
			search_item = i['keyword']
			querystring = {"q": search_item}
			final_url = url + search_url + "/search"
			print(final_url)
			print(querystring)
			response = requests.get(final_url, headers=headers, params=querystring)
			soup = BeautifulSoup(response.content, "lxml")
			table = soup.find('div', attrs={'class': 'rpBJOHq2PR60pnwJlUyP0'})
			for data_id in table.findAll('div', attrs={"class": "_2XDITKxlj4y3M99thqyCsO"}):
				for url in data_id.findAll("a", attrs={"rel": "noopener noreferrer"}):
					print("inside scarpping")
					user_name = data_id.find("a",
											 {"class": "_2tbHP6ZydRpjI44J3syuqC _23wugcdiaj44hdfugIAlnX oQctV4n0yUb0uiHDdGnmE"})
					post_user_name = (user_name.text).split("/")[1]
					post_url = data_id.find("a", {"class": "SQnoC3ObvgnGjWt90zD9Z _2INHSNB8V5eaWp4P0rY_mE"})
					posting_url = "https://www.reddit.com/" + post_url['href']
					post_date = (data_id.find("a", {"class": "_3jOxDPIQ0KaOWpzvSQo-1s"})).text
					posting_date = get_past_date(post_date)
					posting_date_timestamp = datetime.datetime.strptime(posting_date, "%Y-%m-%d").timestamp()
					text = ''
					if 'png' in url['href'] or 'jpeg' in url['href'] or 'jpg' in url['href']:
						text = (data_id.find("div", attrs={"class": "y8HYJ-y_lTUHkQIc1mdCq"})).text
						images = url['href']
						last_images = (url['href'].split("/"))[-1]
						fullfilename = os.path.join(image_path, last_images)
						urllib.request.urlretrieve(images, fullfilename)
						json_data = {
							"username": post_user_name,
							"title": text,
							"subreddit": search_url,
							"keyword": search_item,
							"postingdate": posting_date,
							"postlink": posting_url,
							"image": image_path + "/" + last_images,
							"timestamp": int(datetime.datetime.now().timestamp()),
							"postingtimestamp": int(posting_date_timestamp)
						}
						title_data = db.redditData.find({"title": text}).count()
						if title_data == 0:
							db.redditData.insert(json_data)
						final_list.append({
							"text": text,
							"image": image_path + "/" + last_images
						})
					else:
						for style in data_id.findAll("div", attrs={"class": "_2MkcR85HDnYngvlVW2gMMa"}):
							try:
								stype_image = style.find("div", attrs={
									"class": "_2c1ElNxHftd8W_nZtcG9zf _33Pa96SGhFVpZeI6a7Y_Pl _2e9Lv1I3dOmICVO9fg3uTG"})['style']
								images = (stype_image.split("background-image:url(")[1]).split(");")[0]
							except:
								images = ""

							if 'png' in images or 'jpeg' in images or 'jpg' in images:
								text = (data_id.find("div", attrs={"class": "y8HYJ-y_lTUHkQIc1mdCq"})).text
								last_images = (images.split("/"))[-1]
								fullfilename = os.path.join(image_path,
															last_images)

								urllib.request.urlretrieve(images,
														   fullfilename)
								json_data = {
									"title": text,
									"username": post_user_name,
									"subreddit": search_url,
									"keyword": search_item,
									"postingdate": posting_date,
									"postlink": posting_url,
									"image": image_path + "/" + last_images,
									"timestamp": int(datetime.datetime.now().timestamp()),
									"postingtimestamp": int(posting_date_timestamp)
								}
								title_data = db.redditData.find({"title": text}).count()
								if title_data == 0:
									db.redditData.insert(json_data)
								final_list.append({
									"text": text,
									"image": image_path + "/" + last_images
								})
							else:
								print("eles")
								pass
		except Exception as ex:
			template = "An exception of type {0} occurred. Arguments:\n{1!r}"
			message = template.format(type(ex).__name__, ex.args)
			print(message)
			print("here")
			pass
	d_unique = pd.DataFrame(final_list).drop_duplicates().to_dict('records')
	image_uplode = upload_image(client, d_unique)
	message = {
		"data": "successfully"
	}
	return message


def scrapped_data(request):
	try:
		url = "https://www.reddit.com/r/"
		data = json.dumps(request.POST)
		data = json.loads(data)
		search_url = data['urls']
		search_item = data['search']
		querystring = {"q": search_item}
		final_url = url+search_url+"/search"
		print(final_url)
		response = requests.get(final_url, headers=headers, params=querystring)
		soup = BeautifulSoup(response.content, "lxml")
		table = soup.find('div', attrs={'class': 'rpBJOHq2PR60pnwJlUyP0'})
		for data_id in table.findAll('div', attrs={"class": "_2XDITKxlj4y3M99thqyCsO"}):
			for url in data_id.findAll("a", attrs={"rel": "noopener noreferrer"}):
				print("inside scarpping")
				user_name = data_id.find("a", {"class": "_2tbHP6ZydRpjI44J3syuqC _23wugcdiaj44hdfugIAlnX oQctV4n0yUb0uiHDdGnmE"})
				post_user_name = (user_name.text).split("/")[1]
				post_url = data_id.find("a", {"class": "SQnoC3ObvgnGjWt90zD9Z _2INHSNB8V5eaWp4P0rY_mE"})
				posting_url = "https://www.reddit.com/"+post_url['href']
				post_date = (data_id.find("a", {"class": "_3jOxDPIQ0KaOWpzvSQo-1s"})).text
				posting_date = get_past_date(post_date)
				posting_date_timestamp = datetime.datetime.strptime(posting_date, "%Y-%m-%d").timestamp()
				text = ''
				if 'png' in url['href'] or 'jpeg' in url['href'] or 'jpg' in url['href']:
					text = (data_id.find("div", attrs={"class": "y8HYJ-y_lTUHkQIc1mdCq"})).text
					images = url['href']
					last_images = (url['href'].split("/"))[-1]
					fullfilename = os.path.join(image_path, last_images)
					urllib.request.urlretrieve(images,fullfilename)
					json_data = {
						"username": post_user_name,
						"title": text,
						"subreddit": search_url,
						"keyword": search_item,
						"postingdate": posting_date,
						"postlink": posting_url,
						"image": image_path + "/" + last_images,
						"timestamp": int(datetime.datetime.now().timestamp()),
						"postingtimestamp": int(posting_date_timestamp)
					}
					title_data = db.redditData.find({"title": text}).count()
					if title_data == 0:
						db.redditData.insert(json_data)
					final_list.append({
						"text": text,
						"image": image_path + "/" + last_images
					})
				else:
					for style in data_id.findAll("div", attrs={"class": "_2MkcR85HDnYngvlVW2gMMa"}):
						stype_image = style.find("div", attrs={
							"class": "_2c1ElNxHftd8W_nZtcG9zf _33Pa96SGhFVpZeI6a7Y_Pl _2e9Lv1I3dOmICVO9fg3uTG"})[
							'style']
						images = (stype_image.split("background-image:url(")[1]).split(");")[0]
						if 'png' in images or 'jpeg' in images or 'jpg' in images:
							text = (data_id.find("div", attrs={"class": "y8HYJ-y_lTUHkQIc1mdCq"})).text
							last_images = (images.split("/"))[-1]
							fullfilename = os.path.join(image_path,
														last_images)
							urllib.request.urlretrieve(images,
													   fullfilename)
							json_data = {
								"title": text,
								"username": post_user_name,
								"subreddit": search_url,
								"keyword": search_item,
								"postingdate": posting_date,
								"postlink": posting_url,
								"image": image_path + "/" + last_images,
								"timestamp": int(datetime.datetime.now().timestamp()),
								"postingtimestamp": int(posting_date_timestamp)
							}
							title_data = db.redditData.find({"title": text}).count()
							if title_data == 0:
								db.redditData.insert(json_data)
							final_list.append({
								"text": text,
								"image": image_path + "/" + last_images
							})
						else:
							pass

		print(final_list)
		d_unique = pd.DataFrame(final_list).drop_duplicates().to_dict('records')
		print(d_unique)
		image_uplode = upload_image(client, d_unique)
		# send_mail = requests.post(base_url+"/sendemail/")
		message = {
			"message": "Got the Message",
		}
		return redirect('/')
	except:
		message = {
			"message": "Got the Message",
		}
		return redirect('/')


'''
	Add sub reddint and search to the database for the automatic search
'''
def addsetting(request):
	try:
		last_json = []
		data = json.dumps(request.POST)
		data = json.loads(data)
		search_url = data['urls']
		search_item = data['search']
		reddit_data = db.reddit.find(
			{
				"keyword": search_item,
				"url": search_url,
				"status": 1
			}
		)
		if reddit_data.count() == 0:
			data_reddit = {
				"url": search_url,
				"keyword": search_item,
				"status": 1
			}
			db.reddit.insert(data_reddit)
		return redirect("/setting/")
	except:
		print("exception")
		return redirect("/setting/")


'''
	function for the send the email for the 7 days or once in a week
'''
def my_scheduled_job():
	print("called...!!!")
	currlocal = datetime.datetime.now() - datetime.timedelta(days=7)
	timestamp = datetime.datetime.now().timestamp()
	currentdate = int((currlocal.replace(hour=23, minute=59, second=59, microsecond=59)).timestamp())
	for i in range(len(li)):
		html = ''
		receiver_email = li[i]
		s = smtplib.SMTP('smtp.gmail.com', 587)
		s.starttls()
		s.login(sender_email, "4jN^Dj7Z4dA")
		message = MIMEMultipart("alternative")
		message["Subject"] = "Reddit Report: Keywords and Messages"
		message["From"] = sender_email
		message["To"] = receiver_email
		get_title = db.redditData.find({"timestamp": {"$gte": currentdate, "$lt": timestamp}})
		if get_title.count() > 0:
			count = 1
			for j in get_title:
				user_link = base_url + "/" + j['username']
				print(j['postingdate'])
				html += ' ' + """\
											<html lang="en">
												<head>
													<meta charset="UTF-8" />
													<meta name="viewport" content="width=device-width, initial-scale=1.0" />
													<meta http-equiv="X-UA-Compatible" content="ie=edge" />
													<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css" integrity="sha384-Gn5384xqQ1aoWXA+058RXPxPg6fy4IWvTNh0E263XmFcJlSAwiGgFAW/dAiS6JXm" crossorigin="anonymous"/>
													<style>
													  .heading {
														font-weight: 600;
													  }
													  ul.circle {
														list-style-type: circle;
													  }
													</style>
												</head>
												<body>
												<div class="container">
													<div class="row">
														<div class="col-12 mt-4">
															<p class="heading">Keyword: """ + j['keyword'] + """</p>
															<div class="col-12">
																<p>
																	<a href=""" + j['postlink'] + """>""" + j['title'] + """</a>
																</p>
																<div class="col-12">
																	<ul class="circle">
																		<li>""" + j['title'] + """</li>
																		<li><a href=""" + user_link + """>""" + j[
					'username'] + """</a></li>
																		<li>""" + j['postingdate'] + """</li>
																	</ul>
																</div>
															</div>
														</div>
													</div>
												</div>
												</body>
											</html>
											"""
				count = count + 1
			part1 = MIMEText(html, "html")
			message.attach(part1)
			s.sendmail(sender_email, receiver_email, message.as_string())
	response = {
		"data": "mail send successfully...!!!"
	}
	return response


'''
	API for the send the mail for the user from gmail
'''
class sendemail(APIView):
	def post(self, request):
		print("called...!!!")
		my_scheduled_job()
		response = {
			"data": "mail send successfully...!!!"
		}
		return JsonResponse(response,safe=False, status=200)


def dashboard(request):
	try:
		return render(request, 'reddit/redditPage.html')
	except:
		message = [
			{
				"message": "Internal Server Error"
			}
		]
		return JsonResponse(message, safe=False, status=500)


def settingpage(request):
	try:
		last_json = []
		last_reddit = db.reddit.find({"status": 1}).sort([("_id", -1)])
		if last_reddit.count() > 0:
			for i in last_reddit:
				last_json.append({
					"id": str(i['_id']),
					"reddit": i['url'],
					"keyword": i['keyword']
				})
		else:
			last_json.append({
				"id": "",
				"reddit": "",
				"keyword": ""
			})
		# send_mail = requests.post(base_url+"/sendemail/")
		message = {
			"message": "Got the Message",
		}
		return render(request, 'reddit/settingPage.html', context={"data": last_json})
	except:
		message = [
			{
				"message": "Internal Server Error"
			}
		]
		return JsonResponse(message, safe=False, status=500)


def sendmessage(request, type):
	try:
		user_list = []
		if type == "0":
			get_users = db.redditData.find({}).sort([("_id", -1)])
		else:
			get_users = db.redditData.find({"username": type})
		for i in get_users:
			user_list.append({
				"id": str(i['_id']),
				"name": i['username'],
				"title": i['title'],
				"subreddit": i['subreddit'],
				"keyword": i['keyword'],
				"postingdate": i['postingdate'],
			})
		df = pd.DataFrame(user_list)
		# df = df.drop_duplicates(subset="name", keep="last")
		users = df.to_dict(orient="records")
		return render(request, 'reddit/sendMessage.html', context={"data": user_list})
	except:
		message = [
			{
				"message": "Internal Server Error"
			}
		]
		return JsonResponse(message, safe=False, status=500)


class SendDMUser(APIView):
	def post(self, request):
		try:
			data = request.data
			reddit = praw.Reddit(client_id='P1zvPLvJWju35w',
								 client_secret='NkXwN1LwV14N_wHCIRiTMNELiuE',
								 password='8&D%^34HB.*',
								 user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36',
								 username='SolvngResidntBurnout')
			for i in data['data']:
				data_message = i['message']
				user_data = i['data']
				reddit.redditor(user_data).message('Summary of the week', data_message)
			response = {
				"data": "mail send successfully...!!!"
			}
			return JsonResponse(response, safe=False, status=200)
		except:
			message = [
				{
					"message": "Internal Server Error"
				}
			]
			return JsonResponse(message, safe=False, status=500)


class messagedata(APIView):
	def post(self, request):
		days = int((request.data)['days'])
		user_list = []
		if days == 0:
			get_users = db.redditData.find({}).sort([("_id", -1)])
		else:
			current_time = int(datetime.datetime.now().timestamp())
			last_date = datetime.datetime.now() - datetime.timedelta(days=days)
			last_timestamp = int(last_date.timestamp())
			get_users = db.redditData.find({
				"postingtimestamp": {
					"$gte": last_timestamp,
					"$lte": current_time
				}
			}).sort([("_id", -1)])
		for i in get_users:
			user_list.append({
				"id": str(i['_id']),
				"name": i['username'],
				"title": i['title'],
				"subreddit": i['subreddit'],
				"keyword": i['keyword'],
				"postingdate": i['postingdate'],
			})
		return JsonResponse(user_list, safe=False, status=200)


class DeleteUser(APIView):
	def delete(self, request, *args, **kwargs):
		try:
			productId = kwargs.get('status')
			data = productId.split(',')
			for i in data:
				print(i)
				delete_users = db.redditData.remove({"_id": ObjectId(i)})
			message = {
				"message": "Club Successfully Deleted"
			}
			return JsonResponse(message, safe=False, status=200)
		except:
			message = {
					"message": "Internal Server Error"
				}
			return JsonResponse(message, safe=False, status=500)


class deletereddit(APIView):
	def delete(self, request, *args, **kwargs):
		try:
			productId = kwargs.get('status')
			data = productId.split(',')
			for i in data:
				print(i)
				db.reddit.remove({"_id": ObjectId(i)})
			message = {
				"message": "Reddit Successfully Deleted"
			}
			return JsonResponse(message, safe=False, status=200)
		except:
			message = {
				"message": "Internal Server Error"
			}
			return JsonResponse(message, safe=False, status=500)
