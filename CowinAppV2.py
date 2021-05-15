import hashlib
import smtplib
import winsound
import requests
import time
import json
from datetime import datetime



date = input("Please enter desired slot date (dd-mm-yyyy) eg. 01-12-2020: ")
minAgeLimit = int(input("Please enter an age group (Either 18 or 45): "))
receivers_mail=input("Please enter an email address if required to be notified through an email(else press Enter key): ")
waitSeconds = int(input("Please enter the time to be refreshed(in seconds): "))
flag = 0
stateId = 0
districtId = 0
browser_header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36'}

def sendEmail(content):
    senders_mail = 'xxxxx@gmail.com'
    message = 'Subject: {SUBJECT}\n\n{TEXT}'.format(SUBJECT='Cowin Center found', TEXT=content, indent = 3)
    mail = smtplib.SMTP('smtp.gmail.com',587)
    mail.ehlo()
    mail.starttls()
    mail.login('username','password')
    mail.sendmail(senders_mail,receivers_mail,message)
    mail.close()

def bookAppointment(slot,sessionId):
    mobilenum=input("Please enter your mobile number to generate OTP: ")
    secret="U2FsdGVkX19fpbKmgYmWP/2pcexyF95+gipTb9wwcjir9/P/K3tsOSh6Rw7tU5Ct/JbwK/XBCF8ujGEMAIwBUA=="
    generateOTPurl = "https://cdn-api.co-vin.in/api/v2/auth/generateMobileOTP"
    payload=json.dumps({"mobile":mobilenum, "secret":secret})
    response1=requests.post(generateOTPurl,data=payload,headers=browser_header).json()
    txnId=response1["txnId"]

    otp=input("Please enter the OTP received: ")
    otpSHA = hashlib.sha256(otp.encode('utf-8')).hexdigest()

    confirmOTPurl = "https://cdn-api.co-vin.in/api/v2/auth/validateMobileOtp"
    payload=json.dumps({"otp": otpSHA,"txnId": txnId})
    response2=requests.post(confirmOTPurl,data=payload,headers=browser_header).json()
    token=response2["token"]

    dose=int(input("Please enter 1. For First Dose or 2. For Second Dose : "))
    beneficiariesurl = "https://cdn-api.co-vin.in/api/v2/appointment/beneficiaries"
    jwtHeaders = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36',
      'Authorization': f'Bearer {token}'}
    response3 = requests.request("GET", beneficiariesurl, headers=jwtHeaders)
    beneficiaryData=response3.json()
    if len(beneficiaryData['beneficiaries'])>0:
        count=0
        for i in beneficiaryData['beneficiaries']:
            count+=1
            print(str(count)+".","Beneficiary ID: ",i['beneficiary_reference_id'],"Name: ",i['name'],"Mobile No: ",i['mobile_number'],"Vaccination Status: ",i['vaccination_status'],"\n")
        beneficiariesChoice=input("Please select the members to be added for vaccination separated by space. E.g 1 2 3: ").split()
        beneficiariesList=[]
        for i in beneficiariesChoice:
            beneficiariesList.append(beneficiaryData['beneficiaries'][int(i)-1]['beneficiary_reference_id'])
        payload4=json.dumps({"dose":dose,"session_id": sessionId,"slot":slot,"beneficiaries": beneficiariesList})
        appointmenturl="https://cdn-api.co-vin.in/api/v2/appointment/schedule"
        print("dose: ",dose,"session_id: ", sessionId,"slot: ",slot,"beneficiaries: ",beneficiariesList)
        appointmentBook=input("Please confirm the above details. Press Y to book, N to cancel.").lower()
        if(correctState == 'y'):
            response4 = requests.request("POST", appointmenturl, headers=jwtHeaders, data=payload4).json()
            print(response4)
        return
    
    else:
        print('No beneficiaries found. Please register and add members for vaccination!')
        return


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
        webData1=requests.request("GET", uri, headers=browser_header)
        if webData1.status_code!=200:
                print("Request Blocked: Too much traffic ")
                continue
        webData = webData1.json()
        dataCount = 0
        if(webData["sessions"] or len(webData["sessions"]) > 0):
            for session in webData["sessions"]:
                if(("min_age_limit" not in session)  or session["min_age_limit"] <= minAgeLimit):
                    dataCount += 1
                    print("Option :",dataCount)
                    print("\nCenter ID: ",session["center_id"],"Block: ",session["block_name"],"Pin Code: ",session["pincode"],"Fees: ",session["fee_type"],"Minimum Age: ",session["min_age_limit"]) 
                    print("Available: ",session["available_capacity"],"Vaccine: ",session["vaccine"],"\n")
                    
                    
        if(dataCount == 0):
            print("No slot available.")
        
        else:
            winsound.Beep(3000, 500)
            if len(receivers_mail)>0:
                content=json.dumps(webData["sessions"])
                sendEmail(content)
                
            scheduleCheck=input("Would you like to schedule appointment if possible. Enter Y/N?: ").lower()
            
            if scheduleCheck=="y":
                option=int(input("Please enter the Option number of choice(eg 1,2,etc): "))
                if option>len(webData["sessions"]):
                    continue
                sessionChosen=webData["sessions"][option-1]
                slotNumber=0
                for i in sessionChosen["slots"]:
                    slotNumber+=1
                    print(slotNumber,i)
                slotChosen=int(input("Please enter slot number eg. 1,2,etc: "))
                slot=sessionChosen["slots"][slotChosen-1]
                sessionId=sessionChosen["session_id"]
                bookAppointment(slot,sessionId)
            else:
                continue
        print("LastRefresh: {currentTime}, Age Group: {minAgeLimit} Years, Next Refresh In: {waitSeconds} Seconds".format(currentTime=currentTime,minAgeLimit=minAgeLimit,waitSeconds=waitSeconds))
        print("---------------------------------------------------------")
        
        time.sleep(waitSeconds)
        if flag!=2:
            break


except:
    print("An Error Occurred.")

