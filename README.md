# nikeAPI-Py

30th Jan 2020:     
**Check out https://paname.io my new project !**     
Cloud based bot which currently automate raffles entries.      

-------------------------      

Hi, I'm making public this Nike SNKRS Script I've been working on last year. With work and studies I didn't have time to work on the script these last 6 months and I think I will not have time for anymore so. 

I think the script itself is not working anymore (Nike has shut down a lot of api endpoints) but with a bit of changes like fixing log-in etc... it could be a good script to start with. Anyway a year or so it was working great and I was making a lot of entries on SNKRS with it.
I might upload a nodeJS based-version too soon (more-advanced). 

I'm making it public for the community, hopefully it will help some of you. 
Below I've left some of documentation and WIP. 

Feel free to contact me for any help on it, mail is on my profile and Discord is: **Azerpas#1486**

**Please do not contact me about how to install Python and any other basic, there's a lot of good tutorials on the internet that will explain it better than myself, I'll be happy to help for any other question though** 

If you're making any progress with it let me know, I would love to see what you achieve with this. 

Please excuse my terrible english.

## Documentation

Update 15/12/2018: decoded parts of JS akamai is using for Nike Bot Detection, can't post here for obvious reasons.

**Options**
- [ ] Credit cards every option possible (check when adding new card on SNKRS)
- [ ] PayPal option, very easy
- [ ] Make some international options for EU resident (£, different locations)

## Functions done:
- [x] Authentification with a password
- [x] Getting accounts infos
- [x] Retrieve current calendar
- [x] Find pair into calendar
- [x] Sizes infos
- [x] Retrieve payment infos
- [x] Checkout decomposed parts (4/4)
- [x] Payment parts (2/2)
- [x] Entry
- [x] Checking entry result

###### Authentification with a password
Using grant_type password, submitting accounts email and password to Nike to retrieve an 'access_token' which will be valid for an hour.
It will get the User-id too that might be usefull. 

###### Account infos
Retrieving phone number, checking if verified, phone number country.
nuId and upmId will be scraped too, we will need them for identification checkout. 

###### Calendar
Retrieving current calendar (today's date). I will create some other functions to use the response.

###### Retrieve payment infos
Retrieving payment infos loaded in the current account.
Infos will be re-used in checkout parts.

###### Checkout process
1/4. Checking if payment methods exist.
- I might need to scrape payment id and other ids. 
- I might implement payment methods retrieving or checking if they're the same that the user entered.

2/4. Creating shipping id with uuid.uuid4(): seems to work perfectly fine

3/4. Creating checkout id with uuid.uuid4(): seems to work perfectly fine, and successfully retrieving status
- Device id might be my only problem in this function as I don't know how to generate it, but it random characters seems to suit. Nike won't check on their server.

4/4. Checking if checkout process have been completed with the uuid provided.

###### Payment process
1/2. Posting address + payment method (need to be retrieved when created - technique of delete all payment method and add a new one)
- Retrieving paymentUUID that will be used in 2/2

2/2. Checking if payment has been accepted.

###### Entry process 
1/2. Posting deviceID, checkoutUUID, paymentUUID, launchId, skuUUID, pricechecksum, and every infos.
- Retrieving entryUUID

2/2. Checking win or not with entryUUID.
