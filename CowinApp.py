import smtplib
import winsound
import requests
import time
import json
from datetime import datetime

date = input("Please enter desired slot date (dd-mm-yyyy) eg. 01-12-2020: ")
minAgeLimit = int(input("Please enter an age group (Either 18 or 45): "))
email=input("Please enter an email address if required to be notified through an email: ")
waitSeconds = int(input("Please enter the time to be refreshed(in seconds): "))
flag = 0
stateId = 0
districtId = 0
browser_header = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36'}

try:

    # Find State
        
    while True:
        stateName = input("Please enter state name. E.g. madhya pradesh: ").title()
        uriStates = "https://cdn-api.co-vin.in/api/v2/admin/location/states"
        webDataStates = requests.request("GET", uriStates, headers=browser_header).json()
        dataCount=0
        for i in webDataStates["states"]:
            if stateName == i["state_name"].title():
                stateData=i
                dataCount+=1
        if dataCount==1:
            print("Is this correct state name? ")
            print(stateData["state_name"])
            correctState = input("Y/N?: ").lower()

            if(correctState == 'y'):
                stateId = stateData["state_id"]
                flag = 1
            else:
                print('Try Again.')

        else:
            print('Not able to find exact record. Try Again with another word.')
            
        if(flag!=0):
            break

        
        # Find District
        
    while True:
        districtName = input("Please enter district name. E.g. gwalior: ").title()
        uriDistricts = "https://cdn-api.co-vin.in/api/v2/admin/location/districts/{stateId}".format(stateId=stateId)
        webDataDistricts = requests.request("GET", uriDistricts, headers=browser_header).json()
        dataCount=0
        for i in webDataDistricts["districts"]:
            if districtName == i["district_name"].title():
                districtData=i
                dataCount+=1
                        
        if(dataCount == 1):
        
            print("Is this correct district name? ")
            print(districtData["district_name"])
            correctDistrict=input("Y/N?: ").lower()
            
            if(correctDistrict == 'y'):
                districtId = districtData["district_id"]
                flag = 2
                
            else:
                print('Try Again.')
        
        else:
            print('Not able to find exact record. Try Again with another word.')
            
        if(flag!=1):
                break

                
    # Find slots

    while True:

        currentTime = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
        uri = "https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/findByDistrict?district_id={districtId}&date={date}".format(districtId=districtId,date=date)
        webData = requests.request("GET", uri, headers=browser_header).json()
        dataCount = 0

        if(webData["sessions"] or len(webData["sessions"]) > 0):
            for session in webData["sessions"]:
                if(("min_age_limit" not in session)  or session["min_age_limit"] <= minAgeLimit):
                    print("\nCenter ID: ",session["center_id"],"Block: ",session["block_name"],"Pin Code: ",session["pincode"],"Fees: ",session["fee_type"],"Minimum Age: ",session["min_age_limit"]) 
                    print("Available: ",session["available_capacity"],"Vaccine: ",session["vaccine"],"\n")
                    
                    dataCount += 1
                    
        if(dataCount == 0):
            print("No slot available.")
        
        else:
            winsound.Beep(3000, 500)
            if len(email)>0:
                senders_mail = 'xxxxx@gmail.com'
                receivers_mail=email
                message = 'Subject: {SUBJECT}\n\n{TEXT}'.format(SUBJECT='Cowin Center found', TEXT=json.dumps(webData["sessions"], indent = 3))
                mail = smtplib.SMTP('smtp.gmail.com',587)
                mail.ehlo()
                mail.starttls()
                mail.login('username','password')
                mail.sendmail(senders_mail,receivers_mail,message)
                mail.close()
            

        print("LastRefresh: {currentTime}, Age Group: {minAgeLimit} Years, Next Refresh In: {waitSeconds} Seconds".format(currentTime=currentTime,minAgeLimit=minAgeLimit,waitSeconds=waitSeconds))
        print("---------------------------------------------------------")
        
        time.sleep(waitSeconds)
        if flag!=2:
            break


except:
    print("An Error Occurred.")

