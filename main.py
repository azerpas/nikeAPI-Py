import requests, json
import os , time , random , datetime, sys, uuid
from requests.packages import urllib3
from tabulate import tabulate
urllib3.disable_warnings()

def log(event):
	d = datetime.datetime.now().strftime("%H:%M:%S")
	print("Nike by Azerpas :: " + str(d) + " :: " + event)

user_id = None
access_token = None
PIDpaymentID = None
CC_UUID = None
PCS = None

def login(session,email,password,proxy):
	global user_id
	global access_token
	logindata = {
		'keepMeLoggedIn':True,
		'client_id':'PbCREuPr3iaFANEDjtiEzXooFl7mXGQ7',#'MSgX9SH71y8CYkVjrArZS9EsH4ly1ROG',
		'ux_id':'com.nike.commerce.snkrs.v2.ios',
		'grant_type':'password',
		'username':email,
		'password':password
	}
	a = session.post('https://api.nike.com/idn/shim/oauth/2.0/token',json=logindata,verify=False,proxies=proxy)
	if(a.status_code == 200):
		log("Connected successfully")
	else:
		log("Canno't connect")
		print(a.text)
		raise ValueError("Canno't connect")
	user_id = json.loads(a.text)['user_id']
	access_token = json.loads(a.text)['access_token']
	log("User id: " + user_id + " - Access token: " + access_token)
    
    
def changePassword(session,oldpassword,password,user_id,access_token,proxy):
	changedata = {
		"password":oldpassword,
		"newPassword":password,
		"passwordConfirm":password
	}

	headers = {
		"authority":"www.nike.com",
		"method":"PUT",
		"path":"/profile/services/users/"+user_id+"/password",
		"scheme":"https",
		"accept":"application/json, text/javascript, */*; q=0.01",
		"accept-encoding":"gzip, deflate, br",
		"accept-language":"fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7",
		"Authorization":"Bearer "+access_token,
		"content-locale":"fr_FR",
		"content-type":"application/json",
		"origin":"https://www.nike.com",
		"referer":"https://www.nike.com/fr/fr_fr/p/settings",
		"user-agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36",
		"x-requested-with":"XMLHttpRequest",
	}

	b = session.put("https://www.nike.com/profile/services/users/"+user_id+"/password",json=changedata,headers=headers,proxies=proxy)
	if(b.status_code == 200):
		log("Changed password successfully")
	else:
		log("Canno't change password")
		print(b.text)
		raise ValueError("Canno't change password")

def accountInfos(session,proxy):
	global access_token
	global user_id
	infos_url = "https://api.nike.com/user/commerce"
	headers = {
		"method":"GET",
		"scheme":"https",
		"path":"/user/commerce",
		"authority":"api.nike.com",
		"Authorization":"Bearer "+access_token,
		"content-type":"application/json",
		"accept":"*/*",
		"x-nike-ux-id":"com.nike.commerce.snkrs.v2.ios",
		"user-agent":"SNEAKRS/1.1.3 (iPhone; iOS 11.2.2; Scale/3.00)",
		"x-requested-with":"XMLHttpRequest",
	}
	try:
		a = session.get(infos_url,verify=False,headers=headers)
	except Exception as e:
		log("Canno't connect, means you're banned or your internet isn't working")
		raise e
	if(a.status_code == 200):
		log("Successfully scraped user infos")
	else:
		log("Canno't scrape user infos, please check the password, identification might failed")
		print(a.text)
		raise ValueError("Canno't scrape user infos (error 101)")
	decoded_resp = json.loads(a.text)
	try:
		phoneNumber = decoded_resp['verifiedphone']
		phoneCountry = decoded_resp['verifiedPhoneCountry']
		# just as infos for user
		log("Verified phone number for this account: " + str(phoneNumber) + " : " + str(phoneCountry))
	except Exception as e:
		log("Canno't scrape verified phone neither country, it probably means that this account is not verified, please check the error below")
		print(e)
	try:
		nuId = decoded_resp['nuId']
		upmId = decoded_resp['upmId']
		# both will be used when checking out 
		log("Account infos: " + nuId + " - " + upmId)
	except Exception as e:
		log("Canno't scrape nuId or upmId, it probably means that the login didn't work, please check the error below and retry")
		exit(0)

def getCalendar(session,proxy):
	#"https://api.nike.com/commerce/productfeed/products/snkrs/threads?country=FR&lastUpdatedAfter=2018-03-25-00-00&limit=50&locale=fr_FR&skip=0&withCards=true"
	today = datetime.datetime.now().strftime("%Y-%m-%d-00-00")
	calendar_url = "https://api.nike.com/commerce/productfeed/products/snkrs/threads?country=FR&lastUpdatedAfter=" + today + "&limit=50&locale=fr_FR&skip=0&withCards=true"
	a = session.get(calendar_url,verify=False)
	decoded_resp = json.loads(a.text,encoding="utf-8")
	# you can do whatever you want with this
	return decoded_resp;

def formatedCalendar(text):
	items = []
	for i in text['threads']:
		item = []

		sku = i['product']['style'] +"-"+ i['product']['colorCode']
		try:
			price = i['product']['price']['fullRetailPrice']
		except:
			price = 0
		try:
			commerceDate = i['product']['commerceStartDate']
			title = i['seoTitle'].replace("&amp;","&")
			date = commerceDate.split("T")[0].split("-")
			day = date[2]
			month = date[1]
			year = date[0]
			time = commerceDate.split("T")[1].split(":")
			resultH = time[0]
			resultM = time[1]
		except:
			resultH = ""
			resultM = ""
			day = ""
			month = ""
			year = ""

		item.append(sku)
		item.append(title)
		item.append(price)
		item.append(resultH+":"+resultM)
		item.append(day+":"+month+":"+year)

		items.append(item)

	print (tabulate(items, headers=['sku', 'title', 'price', 'time', 'date']))


def findPairs(calendar,style,keywords,uuid):
	for i in calendar['threads']:
		if(style != ""):
			try:
				if(i['product']['style'] == style):
					log("Found product with input style")
					return i
			except:
				pass
		if(keywords != []):
			for k in keywords:
				try:
					if(k.lower() in i['product']['fullTitle']):
						log("Found product with input keywords")
						return i
				except:
					pass
		if(uuid != ""):
			try:
				if(i['product']['id'] == uuid):
					log("Found product with input uuid")
					return i
			except:
				pass
	log("Can't find any matching product")
			
def getPairInfos(product):
	try:
		thread_id = product['id']
	except:
		log("Can't scrape thread id")
	try:
		short_name = product['name']
	except:
		log("Can't scrape short name")
	try:
		uuid_pair = product['product']['id']
	except:
		log("Can't scrape uuid")
	try:
		style_sku = product['product']['style']
	except:
		log("Can't scrape style sku")
	try:
		pid_pair = product['product']['globalPid']
	except:
		log("Can't scrape pid")
	try:
		full_name = product['product']['fullTitle']
	except:
		log("Can't scrape full name")
	try:
		image_url = product['product']['imageURL']
	except:
		log("Can't scrape image")
	try:
		price = product['product']['price']['fullRetailPrice']
	except:
		log("Can't scrape price")
	try:
		release_date = product['product']['startSellDate']
	except:
		log("Can't scrape release date")
	try:
		maxQuantity = product['product']['quantitylimit']
	except:
		log("Can't scrape max quantity")
	try:
		drawType = product['product']['selectionEngine']
	except:
		log("Can't scrape draw type")
	try:
		waitline = product['product']['waitlineEnabled']
	except:
		log("Can't scrape waitline type")
	try:
		skus = product['product']['skus']
	except:
		log("Can't scrape waitline skus")
	# to:do, select size by keywords entered by user, easy

def liveStock(session,proxy,uuid):
	liveS_url = "https://api.nike.com/deliver/available_skus/v1?filter=productIds("+uuid+")"
	a = session.get(liveS_url,verify=False)
	decoded_resp = json.loads(a.text)
	sizes = decoded_resp['objects']
	# todo20, compare sizes to calendar sizes

def retrievePayMethods(session,proxy,profile):
	global access_token
	global user_id
	global PIDpaymentID

	headers = {
		"authority":"api.nike.com",
		"method":"POST",
		"path":"/commerce/storedpayments/consumer/storedpayments?currency=EUR&includeBalance=true",
		"scheme":"https",
		"accept":"*/*",
		"accept-encoding":"gzip;q=1.0, compress;q=0.5",
		"accept-language":"fr-FR;q=1.0, en-US;q=0.9, zh-Hans-FR;q=0.8",
		"Authorization":"Bearer "+access_token,
		"content-locale":"fr_FR",
		"content-type":"application/json",
		"user-agent":"SNEAKRS/1.1.3 (iPhone; iOS 11.2.2; Scale/3.00)",
		"x-nike-caller-id":"nike:sneakrs:ios:1.1",
	}
	a = session.post('https://api.nike.com/commerce/storedpayments/consumer/storedpayments?currency=EUR&includeBalance=true',verify=False,headers=headers,json={})
	if(a.status_code == 200):
		log("Retrieved payment methods successfully")
		print(a.text)
	else:
		log("Canno't retrieve payment methods")
		print(a.text)
		raise ValueError("Canno't retrieve payment methods")
	try:
		payments = json.loads(a.text)['payments']
		PIDpaymentID = json.loads(a.text)['payments'][0]['paymentId']
		log("PaymentID retrieved")
		return payments
	except Exception as e:
		log("No payment methods found")
		print(e)

def co1(session,proxy,total,item_uuid):
	global access_token
	global user_id

	'''
	x-b3-traceid	7845535027403799357
	x-newrelic-id	VQYGVF5SCBAEVVBUBgMDVg==
	'''
	headers = {
		"authority":"api.nike.com",
		"method":"POST",
		"path":"/payment/options/v2",
		"scheme":"https",
		"accept":"*/*",
		"accept-encoding":"gzip;q=1.0, compress;q=0.5",
		"accept-language":"fr-FR;q=1.0, en-US;q=0.9, zh-Hans-FR;q=0.8",
		"Authorization":"Bearer "+access_token,
		"content-type":"application/json",
		"user-agent":"SNEAKRS/1.1.3 (iPhone; iOS 11.2.2; Scale/3.00)",
		"x-nike-caller-id":"nike:sneakrs:ios:1.1",
	}

	payload = {
		"total": total,
		"items": [item_uuid],
		"billingCountry": "FR",
		"currency": "EUR",
		"country": "FR"
	}

	a = session.post('https://api.nike.com/payment/options/v2',verify=False,headers=headers,json=payload)
	if(a.status_code == 200):
		log("Checkout 1/4")
		#print(a.text)
	else:
		log("Problem while trying to pass 1/4 checkout phase")
		print(a.text)
		raise ValueError("1/4 checkout (error 612)")
	try:
		paymentsOptions = json.loads(a.text)['paymentOptions']
	except Exception as e:
		log("No payment options found")
		print(e)

def co2(session,proxy,item_uuid,sku_uuid,profile):
	global access_token
	global user_id

	'''
	x-b3-traceid	3740821007608208046
	x-newrelic-id	VQYGVF5SCBAEVVBUBgMDVg==
	'''

	headers = {
		"authority":"api.nike.com",
		"method":"POST",
		"path":"/buy/shipping_options/v2",
		"scheme":"https",
		"accept":"application/json",
		"accept-encoding":"gzip;q=1.0, compress;q=0.5",
		"accept-language":"fr-FR;q=1.0, en-US;q=0.9, zh-Hans-FR;q=0.8",
		"Authorization":"Bearer "+access_token,
		"content-type":"application/json; charset=utf-8",
		"user-agent":"SNEAKRS/1.1.3 (iPhone; iOS 11.2.2; Scale/3.00)",
		"x-nike-caller-id":"nike:sneakrs:ios:1.1",
	}

	shippingUUID = str(uuid.uuid4())
	
	payload = {
		"items": [{
			"id": shippingUUID,
			"shippingAddress": {
				"postalCode": profile['zip'],
				"address1": profile['address'],
				"city": profile['city'],
				"country": "FR"
			},
			"skuId": sku_uuid
		}],
		"currency": "EUR",
		"country": "FR"
	}

	a = session.post('https://api.nike.com/buy/shipping_options/v2',verify=False,headers=headers,json=payload)
	if(a.status_code == 200):
		log("Checkout 2/4")
		#print(a.text)
	else:
		log("Problem while trying to pass 2/4 checkout phase")
		print(a.text)
		raise ValueError("2/4 checkout (error 613)")
	try:
		items = json.loads(a.text)['items']
		return shippingUUID
	except Exception as e:
		log("Shipping options canno't be submit")
		print(e)

def co3(session,proxy,sku_uuid,profile,shippingUUID,deviceId):
	global access_token
	global user_id

	checkoutUUID = str(uuid.uuid4())

	headers = {
		"authority":"api.nike.com",
		"method":"PUT",
		"path":"/buy/checkout_previews/v2/"+checkoutUUID,
		"scheme":"https",
		"accept":"application/json",
		"accept-encoding":"gzip;q=1.0, compress;q=0.5",
		"accept-language":"fr-FR;q=1.0, en-US;q=0.9, zh-Hans-FR;q=0.8",
		"Authorization":"Bearer "+access_token,
		"content-type":"application/json",
		"user-agent":"SNEAKRS/1.1.3 (iPhone; iOS 11.2.2; Scale/3.00)",
		"x-nike-caller-id":"nike:sneakrs:ios:1.1",
	}

	payload = 	{
		"request": {
			"email": profile['email'],
			"clientInfo": {
				"deviceId": deviceId,
				"client": "com.nike.commerce.snkrs.v2.ios"
			},
			"currency": "EUR", #todo
			"items": [{
				"recipient": {
					"lastName": profile['lname'],
					"firstName": profile['fname']
				},
				"shippingAddress": {
					"city": profile['city'],
					"address1": profile['address'],
					"postalCode": profile['zip'],
					"country": "FR"
				},
				"id": shippingUUID,
				"quantity": 1,
				"skuId": sku_uuid,
				"shippingMethod": "GROUND_SERVICE",
				"contactInfo": {
					"phoneNumber": profile['phone'],
					"email": profile['email']
				}
			}],
			"channel": "SNKRS",
			"locale": "fr_FR",
			"country": "FR"
		}
	}

	a = session.put('https://api.nike.com/buy/checkout_previews/v2/'+checkoutUUID,verify=False,headers=headers,json=payload)
	if(a.status_code == 202):
		log("Checkout 3/4")
		#print(a.text)
	else:
		log("Problem while trying to pass 3/4 checkout phase")
		print(a.text)
		raise ValueError("3/4 checkout (error 614)")
	try:
		status = json.loads(a.text)['status']
		log("Status: " + status)
		return checkoutUUID
	except Exception as e:
		log("Checkout preview canno't be submit")
		print(e)

def co4(session,proxy,checkoutUUID):
	global access_token
	global user_id
	global PCS

	headers = {
		"authority":"api.nike.com",
		"method":"GET",
		"path":"/buy/checkout_previews/v2/jobs/"+checkoutUUID,
		"scheme":"https",
		"accept":"application/json",
		"accept-encoding":"gzip;q=1.0, compress;q=0.5",
		"accept-language":"fr-FR;q=1.0, en-US;q=0.9, zh-Hans-FR;q=0.8",
		"Authorization":"Bearer "+access_token,
		"content-type":"application/json; charset=UTF-8",
		"user-agent":"SNEAKRS/1.1.3 (iPhone; iOS 11.2.2; Scale/3.00)",
		"x-nike-caller-id":"nike:sneakrs:ios:1.1",
	}


	checkout_url = "https://api.nike.com/buy/checkout_previews/v2/jobs/"+checkoutUUID
	a = session.get(checkout_url,verify=False, headers=headers)
	#print(a)
	#print(a.text)
	decoded_resp = json.loads(a.text)
	try:
		status = decoded_resp['status']
	except:
		return False
	if(status=="COMPLETED"):
		PCS = decoded_resp['response']['priceChecksum']
		return True
	else:
		return False

def userCheck(session,proxy,password):
	global access_token
	global user_id
	headers = {
		"authority":"api.nike.com",
		"method":"POST",
		"path":"/userCheck",
		"scheme":"https",
		"accept":"*/*",
		"accept-encoding":"gzip;q=1.0, compress;q=0.5",
		"accept-language":"fr-FR;q=1.0, en-US;q=0.9, zh-Hans-FR;q=0.8",
		"Authorization":"Bearer "+access_token,
		"content-type":"application/json",
		"user-agent":"SNEAKRS/1.1.3 (iPhone; iOS 11.2.2; Scale/3.00)",
		"x-nike-ux-id":"com.nike.commerce.snkrs.v2.ios",
	}

	payload = {
	"password": password
	}

	a = session.post("https://api.nike.com/userCheck",verify=False,headers=headers,json=payload)
	if(a.status_code == 200):
		log("User checked successfully")
		#print(a.text)
	else:
		log("Can't check user")
		print(a.text)
		raise ValueError("Can't check user (error 344)")
	try:
		nuId = json.loads(a.text)['nuId']
		upmId = json.loads(a.text)['upmId']
	except Exception as e:
		log("Can't retrieve nuId or upmId")
		print(e)

def pay1(session,proxy,total,item_uuid,profile,checkoutId):#,paymentInfo):
	global user_id
	global access_token

	headers = {
		"authority":"api.nike.com",
		"method":"POST",
		"path":"/payment/preview/v2",
		"scheme":"https",
		"accept":"application/json; charset=utf-8",
		"accept-encoding":"gzip;q=1.0, compress;q=0.5",
		"accept-language":"fr-FR;q=1.0, en-US;q=0.9, zh-Hans-FR;q=0.8",
		"Authorization":"Bearer "+access_token,
		"content-type":"application/json",
		"user-agent":"SNEAKRS/1.1.3 (iPhone; iOS 11.2.2; Scale/3.00)",
		"x-nike-caller-id":"nike:sneakrs:ios:1.1",
	}

	payload = {
	"total": total,
	"items": [{
		"productId": item_uuid,
		"shippingAddress": {
			"city": profile['city'],
			"address1": profile['address'],
			"postalCode": profile['postalCode'],
			"country": "FR" #todo18
		}
	}],
	"checkoutId": checkoutId,
	"currency": "EUR",
	"paymentInfo": [{
		"id": PIDpaymentID,
		"cardType": "MasterCard",
		"accountNumber": "XXXXXXXXXXXX"+paymentInfo['accountNumber'][-4:],
		"creditCardInfoId": CC_UUID,
		"type": "CreditCard",
		"paymentId": PIDpaymentID,
		"billingInfo": {
			"name": {
				"lastName": profile['lname'],
				"firstName": profile['fname']
			},
			"contactInfo": {
				"phoneNumber": profile['phone'],
				"email": profile['email']
			},
			"address": {
				"city": profile['city'],
				"address1": profile['address'],
				"postalCode": profile['zip'],
				"country": "FR"
			}
		}
	}],
	"country": "FR"
	}

	a = session.post('https://api.nike.com/payment/preview/v2',verify=False,headers=headers,json=payload)
	if(a.status_code == 202):
		log("Payment 1/2")
		print(a.text)
	else:
		log("Problem while trying to pass 1/2 payment phase")
		print(a.text)
		raise ValueError("1/2 payment (error 615)")
	try:
		status = json.loads(a.text)['status']
		paymentID = json.loads(a.text)['id']
		log("Status: " + status)
		log("Payment: " + paymentID)
		return paymentID
	except Exception as e:
		log("Payment preview canno't be submit")
		print(e)

def pay2(session,proxy,paymentUUID):
	global access_token
	global user_id

	headers = {
		"authority":"api.nike.com",
		"method":"GET",
		"path":"/payment/preview/v2/jobs/"+paymentUUID,
		"scheme":"https",
		"accept":"application/json; charset=utf-8",
		"accept-encoding":"gzip;q=1.0, compress;q=0.5",
		"accept-language":"fr-FR;q=1.0, en-US;q=0.9, zh-Hans-FR;q=0.8",
		"Authorization":"Bearer "+access_token,
		"content-type":"application/json; charset=UTF-8",
		"user-agent":"SNEAKRS/1.1.3 (iPhone; iOS 11.2.2; Scale/3.00)",
		"x-nike-caller-id":"nike:sneakrs:ios:1.1",
	}


	#checkout_url = "https://api.nike.com/payment/preview/v2/jobs/"+checkoutUUID
	a = session.get("https://api.nike.com/payment/preview/v2/jobs/"+paymentUUID,verify=False, headers=headers)
	print(a)
	print(a.text)
	decoded_resp = json.loads(a.text)
	try:
		status = decoded_resp['status']
	except:
		return False
	if(status=="COMPLETED"):
		return True
	else:
		return False

def entry1(session,proxy,profile,deviceId,checkoutUUID,paymentUUID,sku_uuid,priceChecksum,launchId):
	global access_token
	global user_id

	headers = {
		"authority":"api.nike.com",
		"method":"POST",
		"path":"/launch/entries/v2",
		"scheme":"https",
		"accept":"*/*",
		"accept-encoding":"gzip;q=1.0, compress;q=0.5",
		"accept-language":"fr-FR;q=1.0, en-US;q=0.9, zh-Hans-FR;q=0.8",
		"Authorization":"Bearer "+access_token,
		"content-type":"application/json",
		"user-agent":"SNEAKRS/1.1.3 (iPhone; iOS 11.2.2; Scale/3.00)",
		"x-nike-caller-id":"nike:sneakrs:ios:1.1",
	}

	payload = {
	"deviceId": deviceId,
	"checkoutId": checkoutUUID,
	"currency": "EUR",
	"paymentToken": paymentUUID,
	"shipping": {
		"recipient": {
			"lastName": profile['lname'],
			"firstName": profile['fname'],
			"email": profile['email'],
			"phoneNumber": profile['phone']
		},
		"method": "GROUND_SERVICE",
		"address": {
			"city": profile['city'],
			"address1": profile['address'],
			"postalCode": profile['zip'],
			"country": "FR"
		}
	},
	"skuId": sku_uuid,# "df9a23e7-a549-5cb4-91a2-fca03224de28",
	"channel": "SNKRS",
	"launchId": launchId, # "acedd90d-a7fd-449b-a1fa-149abeade37e",
	"locale": "fr_FR",
	"priceChecksum": priceChecksum, #"5492053f735d2ea35dcb6a1f10eca05c"
	}


	a = session.post('https://api.nike.com/launch/entries/v2',verify=False,headers=headers,json=payload)
	if(a.status_code == 201):
		log("Entry 1/2")
		print(a.text)
	else:
		log("Problem while trying to pass 1/2 entry phase")
		print(a.text)
		raise ValueError("1/2 entry (error 715)")
	try:
		entryId = json.loads(a.text)['id']
		log("entryId: " + entryId)
		return entryId
	except Exception as e:
		log("Entry canno't be submit")
		print(e)

def entry2(session,proxy,entryUUID):
	global access_token
	#"estimatedResultAvailability": "2018-03-26T08:03:03.000Z",

	'''
	"result": {
		"checkoutId": "bb4b5731-1935-4785-b208-65f38e9988d7",
		"status": "NON_WINNER",
		"reason": "OUT_OF_STOCK",
		"reentryPermitted": true
	},
	'''

	headers = {
		"authority":"api.nike.com",
		"method":"GET",
		"path":"/launch/entries/v2/"+entryUUID,
		"scheme":"https",
		"accept":"*/*",
		"accept-encoding":"gzip;q=1.0, compress;q=0.5",
		"accept-language":"fr-FR;q=1.0, en-US;q=0.9, zh-Hans-FR;q=0.8",
		"Authorization":"Bearer "+access_token,
		"content-type":"application/json",
		"user-agent":"SNEAKRS/1.1.3 (iPhone; iOS 11.2.2; Scale/3.00)",
		"x-nike-caller-id":"nike:sneakrs:ios:1.1",
	}

	a = session.get("https://api.nike.com/launch/entries/v2/"+entryUUID,verify=False, headers=headers)
	print(a)
	print(a.text)
	decoded_resp = json.loads(a.text)
	try:
		time = decoded_resp['estimatedResultAvailability']
		time = time.split("T")[1]
		time = time.split(":")
		resultH = time[0]
		resultM = time[1]
		resultS = time[2][:2]
		log("Waiting for result till: " + str(resultH) + ":" + str(resultM) + ":" + str(resultS))
		schedule((int(resultH)-2),int(resultM),int(resultS))
		return 'wait'
		# transformer les valeurs en Int et ajouter scheduler puis entry2()
		# schedule(int(resultH),int(resultM),int(resultS))
	except:
		try:
			drawResult = decoded_resp['result']['status'] ####???????????
			log("Result: "+drawResult)
			return drawResult
		except:
			log("Can't fetch result")
			print(decoded_resp)
			return 'looser'

		# alors resultat disponible, donc result['status'] -- result['reason'] -- result['reentryPermitted']
		# encore un try -- except alors


	##########
	# NEED TO DELETE EVERY CARD AND REPOST  CARD

def schedule(hour,minu,sec):
	for i in xrange(0, 365):
		t = datetime.datetime.today()
		future = datetime.datetime(t.year, t.month, t.day, hour, minu, sec)
		if t.hour >= 2:
			future += datetime.timedelta(days=1)
		time.sleep((future - t).seconds)


def setPayment(session,proxy,profile):
	global access_token
	global user_id

	payments = retrievePayMethods(session,proxy,profile)
	if(payments):
		for i in payments:
			paymentID = i['paymentId']
			# usual headers
			headers = {
			"authority":"api.nike.com", "method":"DELETE","path":"/commerce/storedpayments/consumer/storedpayments/"+paymentID,
			"scheme":"https","accept":"*/*","accept-encoding":"gzip;q=1.0, compress;q=0.5","accept-language":"fr-FR;q=1.0, en-US;q=0.9, zh-Hans-FR;q=0.8",
			"Authorization":"Bearer "+access_token, "content-type":"application/json","user-agent":"SNEAKRS/1.1.3 (iPhone; iOS 11.2.2; Scale/3.00)",
			"x-nike-caller-id":"nike:sneakrs:ios:1.1",
			}
			r = session.delete("https://api.nike.com/commerce/storedpayments/consumer/storedpayments/"+paymentID,verify=False,headers=headers)
			print(r)
			print(r.text)
			if(r.status_code == 204):
				log("Successfully deleted paymentID: " + paymentID)
			else:
				log("There was a problem while trying to delete paymentID:" + paymentID)
				
	newPaymentID = str(uuid.uuid4()).upper()
	headers = {
		"authority":"api.nike.com", "method":"POST","path":"/paymentcc/creditcardsubmit/creditcardsubmit/"+newPaymentID+"/store",
		"scheme":"https","accept":"*/*","accept-encoding":"gzip;q=1.0, compress;q=0.5","accept-language":"fr-FR;q=1.0, en-US;q=0.9, zh-Hans-FR;q=0.8",
		"Authorization":"Bearer "+access_token, "content-type":"application/json","user-agent":"SNEAKRS/1.1.3 (iPhone; iOS 11.2.2; Scale/3.00)",
		"x-nike-caller-id":"nike:sneakrs:ios:1.1",
	}

	payload = {
		"cvNumber": paymentInfo['cvNumber'],
		"accountNumber": paymentInfo['accountNumber'],
		"expirationYear": paymentInfo['expirationYear'],
		"cardType": paymentInfo['cardType'],
		"expirationMonth": paymentInfo['expirationMonth']
	}
	r = session.post("https://api.nike.com/paymentcc/creditcardsubmit/creditcardsubmit/"+newPaymentID+"/store",verify=False,headers=headers,json=payload)
	print(r)
	headers = {
		"authority":"api.nike.com", "method":"GET","path":"/paymentcc/creditcardsubmit/creditcardsubmit/"+newPaymentID+"/isValid",
		"scheme":"https","accept":"*/*","accept-encoding":"gzip;q=1.0, compress;q=0.5","accept-language":"fr-FR;q=1.0, en-US;q=0.9, zh-Hans-FR;q=0.8",
		"Authorization":"Bearer "+access_token, "content-type":"application/json","user-agent":"SNEAKRS/1.1.3 (iPhone; iOS 11.2.2; Scale/3.00)",
		"x-nike-caller-id":"nike:sneakrs:ios:1.1",
	}
	r2 = session.get("https://api.nike.com/paymentcc/creditcardsubmit/creditcardsubmit/"+newPaymentID+"/isValid",verify=False,headers=headers)
	print(r2)

	headers = {
		"authority":"api.nike.com", "method":"POST","path":"/commerce/storedpayments/consumer/savepayment",
		"scheme":"https","accept":"*/*","accept-encoding":"gzip;q=1.0, compress;q=0.5","accept-language":"fr-FR;q=1.0, en-US;q=0.9, zh-Hans-FR;q=0.8",
		"Authorization":"Bearer "+access_token, "content-type":"application/json","user-agent":"SNEAKRS/1.2.2 (iPhone; iOS 11.2.2; Scale/3.00)",
		"x-nike-caller-id":"nike:sneakrs:ios:1.2",
	}

	payload = {
		"isDefault": "false",
		"creditCardInfoId": newPaymentID,
		"type": "CreditCard",
		"billingAddress": {
			"city": profile['city'],
			"address1": profile['address'],
			"postalCode": profile['zip'],
			"phoneNumber": profile['phone'],
			"email": profile['email'],
			"lastName": profile['lname'],
			"firstName": profile['fname'],
			"country": "FR"
		},
		"currency": "EUR"
	}

	r3 = session.post("https://api.nike.com/commerce/storedpayments/consumer/savepayment",verify=False,headers=headers,json=payload)
	print(r3)

	if(r3.status_code != 201):
		log("Error 4515")

	if(r.status_code == 201):
		if(r2.status_code == 200):
			log("Successfully added new payment to your account, newPaymentID: " + newPaymentID)
			return newPaymentID
			# do i have to add something to return -"paymentId" : "pid47391cc2-4206-4f08-919d-42bbd2fb1a29",- ?
			# todo15
		else:
			log("There was a problem while trying to verify if payment is valid (Error 2134)")
	else:
		log("There was a problem while trying to add a new payment method (Error 9011)")

def getLaunchID(session,proxy,productUUID):
	#https://api.nike.com/launch/launch_views/v2?filter=productId(a06463c7-6c62-5b83-b79f-1c69f5d34e73,be2f17fc-c629-5785-b100-d4cb60278a01,dcc140b0-80ec-5ab2-9ce9-9afa508d898f,0b2410ac-bb99-5330-85dd-18c014474325,d00f855a-c41f-59fc-93b3-690a1857a844,61df791a-b1d7-57c1-a4f6-3bae510ed413,038ee55e-680e-5448-9c12-e4ac93c5ff37,7cb3d5ad-0900-5102-9273-be34312071b3,d303a2d8-547c-508b-94cc-10428e43a32e,b87d3475-ebd3-566d-9aad-6406c11e27a7,e28c6605-09d8-52bc-9b71-34a9d881d61e,b9a97705-5977-5653-b7d7-8292ec603fa0,2b48a9d9-e4cf-579c-8fb9-988e5138b401,1984c803-669c-5b43-9d5d-97c95a137351,01f0c4be-5cfb-56ce-89f3-ea4c6d42ebe8,e453d1e1-d448-5779-bb68-646bb328b4d4,fc65eafd-b440-5bd0-b8ab-9e616304a26d,0febc47a-9aea-50f2-bff7-c78e6727d980,55f2ff6b-2258-5141-8e49-921cc8033431,7d993144-13a6-5cb3-bdfb-f59604e39e58,a49e09e4-de08-52c6-8739-eb8bf5ab7a9d,5c007699-b81c-5f1c-845d-9080b1590184)
	global access_token
	global user_id

	launch_url = "https://api.nike.com/launch/launch_views/v2?filter=productId("+productUUID+")"
	a = session.get(launch_url,verify=False)
	decoded_resp = json.loads(a.text,encoding="utf-8")
	return decoded_resp['objects'][0]['id']

hour = 19
minu = 46
sec = 00


s = requests.session()
proxy = {'https' : ''}

log("Waiting till: " + str(hour) + ":" + str(minu))
#schedule(hour,minu,sec)

login(s,"sushi@gmail.com","123456",proxy)

profile = {
	'zip':'77777', 'address':'1 Rue De la Berge', 'city':'Paris','phone':'646123984',
	'lname':'PAS','fname':'AZER','email':'AZER@gmail.com','password':''
}

paymentInfo = {
	"cvNumber": "000",
	"accountNumber": "4974970013330000",
	"expirationYear": "2022",
	"cardType": "UNKNOWN", # ? mastercard visa etc? check SNKRS
	"expirationMonth": "01"
}

deviceId = "0500Eit1Aks166fErl0+1uL24qSxO4aEE18ghxXFbqXRnnuyPBqyN19uaGXZIHBuKG\/aUP1MxcsCsaeJVPkOG9WjujlxYtGtOmhVPZiB3G\/Z2peYCWI3GQKtEQSdPHaEZDuR\/KjT1k\/j978OTtSVGP5NSz99g7EZLoEll\/a8im45O8\/qz34bGDcfMVX\/HBFE7ScPJDmdjYymHK6MoqwAJw83f6EMnNMzkmb+OR+UXuf5hzkiVHAZCDkZBa23eIVfu5w+i1pLZczUYzhAhyQVz6dsjBhH3vn6fUaOtK3MzPh1P0UN48PB\/v1j31NoGKmIHgAIJnGTsHlfhzU+dnSs8eZqpF99veg44dZ2E+Kblfjrji0+Y585TFTVfM5WxKtZlZwZAtYsnxv7h\/pEHKneCVCoyXkwNkgHECiI3yUtLrYxMi8X+oZnJLmzaJiBWQjmfFDSqChPFDHt3PJpCy2kbLPlTjHt6wBEyS3019GB5XxcrYvYXL0AVgeGznsHAunMzueORQmtwnPmIuI9dzHmQ6sCmNViPcvwdfKb2AndeTI8uraDu\/VYHu5K1DHmO2kA0M8SEpKIv0zrAHaFxQAmmDh0nVjPF\/JdRPfbLR+Qgtjn9H3mDojNLeJ8V\/mkaNJ6PpRMn+hPi421eewvfCeRxxjZTbFs8cyp5Xo7O8JDX+Sy2nZNHlGo565hs7pmS6YzQa0qPDm1OjwsC8z+JIs6izdlR+7Dsxf3vuZ0vkj1F6CzHlyklfgbfQ0LBCxFIVMuRXZq0efOogUAC7fFDr2H3gwwk7MNslGKQvNwwqCwBcNXtU9VeEh7fFNwtfXU6FJJbxZJSvweLbuU3RXOITrp+ubPFElB4ySLKIRIYmkK\/o0XrRFJ7aU\/QF97zE5D9LhQ2ZJenA0HB+WivcHitrFRl6rNopnnt1YyYSPSrtwrLf\/iS6ZMsSv7GohuMM1WWGcj4A1tb40pSjCCpmU6C9fXpoXrmMcoSVkjHT5pTnNSWX62M2teUBMYv72SD5HZD4fkLtAJ9jvs9hD2+HB57HGrKxPpwSOJrV+lVZsw07FKybAMG6dt498jMVTMuGkmxOhqAkOvfL5TYZXbdJYPX793vkUvskuwlRzGnr0uqWv7n7tl0s0AFQFgAAHBORqpVuFDr6SQ2GzSruGhfQudju+1OqTvjOMem6nt7CHJH1uO9h7xSPy+gYtek6OYYslo+Rq2T7TdDOwgqkd5tGk6D2WtUyp\/qMmVzknmNFX0Wgfm5tUMZGHQzfBZowmuAPLvrzmASOpZJ1dLntMboVCCn0fuJRGrjvl3qX2+MasnDq334tP9puwTZuzVhLQ7ixHq7kLvv8MZozW6BHgs9ACFJnrxciZEWecIHD3b+CdcOlY2fbUKKn0mVomEQ5h9RdVRwOYU3GEs9QWEczR8Va9kfBNl3kRRJJIoWWHx3SOPl5yGysfxASXgPEfQT7Z87cAGB6L4Si89lGsGciAf4DHIdqwBPCI1FhhcYQPsbL60O7dkZomt0d1iRsm0dVPJil9GRL36+PV1GMDbFiK9gQ0f6eBKZBVPc8TatMnHamq2XDmisnUiFmksIIQtT4EHkERXNNt1iP4J7XO1lQp8PFm6yTYLMFFUFo+jcDNkZTrKp5IbmXCS0nRnTGuLsU0uEREWleHZcql283MlL\/e6rIy54+o2wkAcNSM9zlCTOujoemZ4SJHNkaESf3hos\/4ZXW7bQZ5ELmAv4af2DtYkl56k9NPtBL1oXFgEIx21OL60ndj+vhTk4glqGQQxGtw80ow5FyfKOrV\/GeqagWDL5wnWbVvpKbzWQ1QR302koISgC2bH2oTRYr3MS0aiwsfhOfxuH9WMLUfPf9fxQCxxeZL1zzcoHFiS4+gdGp1Ili7QpPDGAXJGd02dlKw0XVHedO0CauQInyxa+xyDQnE4TZoVGWLeDcrlHjQO\/g85Jp2GLwFn2VCC3zJ3GkWGA+3rNLZZALog3MTd6h0tSeBSbF0Na+A+GYeyel26WjzD7NhlkdY2cIyAijewEh\/musEgPRrLzv+3\/qRHtAKtEITeaIV2t\/iNwyK1yAhM1iZYGTrG5xXxEcMnmnaMWRhRfVIGZd6HjTXPZU5ayazspue0Q4+eSvVaPctLmQrikSdTAsn7P4KRzypXrrWMZ20lasLzdiLmH8qavjwUu4wG0OuwvGLqftcJtoHEoH4ClXf7vri8N3xNZR4CRETDzMhML6MzY74ZK1McyMo6xlnuSFrUgOVpnIl6e2QMdz7xUylB6burCR8mWCg26OnX0k01AllSh+f0KD5lkeH9IyCSNzBtkfq2UzIFI1RYlL4R1fNKl6+3F4PQZacpY2mMwM08VK+QL6TlVNpotpBI5KRGOR\/GlpJdTjrtRSAfaXfsMW8+U8AO8dm2rMNb1gRfgj76qzSp3W3xzPURYb4F+yxYZhiFS+lcUbRrrEwE\/V8VudRcQeAoFwBMlQBj5+g5DcAO+IzqHLxNb91XgHL2JsFJzgie2KxWwgWRxeen5LueTFBjKa22AE5ktaCc\/\/Xb1ymVCsi20aqL77nTY8LtTxImyScEXUKXZYz7XjQt+XcV0e4jKomtmcN2gJDw3CEr0HFMJeaT6eIlg5NJRUUtiO9WaO5\/T\/30lLuovz+\/sTK+lBmLclWk6Ttqi1oFJ4cmIqTwloIQzFy9S9JqeFmZ\/qmnGItbIrxjo+Q7zrSHZ1uVWUye5SWPIcXAEjaPSDqKeBRyYhtx6hUsPIEW8wEDrcPYgajS7xnnA+drPzMRpQ=="


productUUID = "e1cf9e72-7020-5e4c-84b6-199bc60c88e1"
skuUUID = "4d4bd851-5ab6-5643-bcc1-7930256c5ca9"
retail = 250

accountInfos(s,proxy)
retrievePayMethods(s,proxy,{})

CC_UUID = setPayment(s,proxy,profile)
retrievePayMethods(s,proxy,{})   #todo16

liveStock(s,proxy,productUUID)
launchID = getLaunchID(s,proxy,productUUID)
co1(s,proxy,retail,productUUID)
shippingUUID = co2(s,proxy,productUUID,skuUUID,profile)
checkoutUUID = co3(s,proxy,skuUUID,profile,shippingUUID,deviceId)
status = co4(s,proxy,checkoutUUID)
if(status):
	log("Completed checkout phase, going to payment phase")
userCheck(s,proxy,"123456")
paymentUUID = pay1(s,proxy,retail,productUUID,profile,checkoutUUID)#,paymentInfo) #item_uuid profile paymentInfo
status2 = pay2(s,proxy,paymentUUID)
if(status2):
	log("Completed payment phase, going to entry phase")
entryUUID = entry1(s,proxy,profile,deviceId,checkoutUUID,paymentUUID,skuUUID,PCS,launchID) # sku uuid launchid pricecheksum
log("Entry id: " + entryUUID)

log("Waiting for draw to end, will scrape results later...")
schedule(datetime.datetime.now().hour,30,30)

response = entry2(s,proxy,entryUUID)

while(response == 'wait'):
	if (response != 'wait'):
		if (response != 'looser'):
			log("Winner! Check your mail!")
			exit(0)
		else:
			log("No win, maybe next time!")
			exit(0)
	reponse = entry2(s,proxy,entryUUID)

