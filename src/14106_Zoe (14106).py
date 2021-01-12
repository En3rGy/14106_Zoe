# coding: UTF-8

import urllib
import urllib2
import ssl
import urlparse
import threading
from datetime import datetime
import json

##!!!!##################################################################################################
#### Own written code can be placed above this commentblock . Do not change or delete commentblock! ####
########################################################################################################
##** Code created by generator - DO NOT CHANGE! **##

class Zoe_14106_14106(hsl20_3.BaseModule):

    def __init__(self, homeserver_context):
        hsl20_3.BaseModule.__init__(self, homeserver_context, "14106_Zoe")
        self.FRAMEWORK = self._get_framework()
        self.LOGGER = self._get_logger(hsl20_3.LOGGING_NONE,())
        self.PIN_I_S_USER=1
        self.PIN_I_S_PW=2
        self.PIN_I_S_VIN=3
        self.PIN_I_N_INTERVAL=4
        self.PIN_I_N_TRIGGER=5
        self.PIN_I_N_AC=6
        self.PIN_I_N_ACTEMP=7
        self.PIN_I_N_CHARGE=8
        self.PIN_O_S_CARPICTURE=1
        self.PIN_O_N_BATTERYLEVEL=2
        self.PIN_O_N_BATTERYAUTONOMY=3
        self.PIN_O_N_BATTERYAVAILABLEENERGY=4
        self.PIN_O_N_BATTERYTEMPERATURE=5
        self.PIN_O_N_PLUGSTATUS=6
        self.PIN_O_N_CHARGESTATUS=7
        self.PIN_O_N_TOTALMILEAGE=8
        self.PIN_O_N_GPSLATITUDE=9
        self.PIN_O_N_GPSLONGITUDE=10
        self.PIN_O_S_LASTUPDATETIME=11
        self.PIN_O_N_ACFEEDBACK=12
        self.FRAMEWORK._run_in_context_thread(self.on_init)

########################################################################################################
#### Own written code can be placed after this commentblock . Do not change or delete commentblock! ####
###################################################################################################!!!##


    g_myRenaultUser = ""     # email
    g_myRenaultPass = ""     # password

    # set your ZOE Model (Phase 1 or 2) // bitte eingeben!
    g_ZOE_Phase = "2" # "1" or "2"

    # optional: 
    # enter your VIN / FIN if you have more than 1 vehicle in your account
    # or if you get any login-errors
    # leave it blank to auto-select it
    g_VIN = "" # starts with VF1... enter like this: "VF1XXXXXXXXX"

    # do not edit
    g_kamareonURL = "https://api-wired-prod-1-euw1.wrd-aws.com"
    g_kamareonAPI = "oF09WnKqvBDcrQzcW1rJNpjIuy7KdGaB"
    g_gigyaURL = "https://accounts.eu1.gigya.com"
    g_gigyaAPI = "3_7PLksOyBRkHv126x5WhHb-5pqC1qFR8pQjxSeLB6nhAnPERTUlwnYoznHSxwX668" # austria: "3__B4KghyeUb0GlpU62ZXKrjSfb7CPzwBS368wioftJUL5qXE0Z_sSy0rX69klXuHy"

    g_keychain = {}


    def clearKeychain(self):
        if('account_id' in self.g_keychain):
            del self.g_keychain['account_id']
        if('gigyaJWTToken' in self.g_keychain):
            del self.g_keychain['gigyaJWTToken']
        if('gigyaCookieValue' in self.g_keychain):
            del self.g_keychain['gigyaCookieValue']
        if('gigyaPersonID' in self.g_keychain):
            del self.g_keychain['gigyaPersonID']
        if('gigyaGigyaDataCenter' in self.g_keychain):
            del self.g_keychain['gigyaGigyaDataCenter']


    def getDate(self):
        now = datetime.now()
        timenow = now.strftime("%Y%m%d-%H") # shall: "20201028-14" (14 = hour)
        return timenow


    def checkTime(self):
        if('lastJWTCall' in self.g_keychain):
            if (self.g_keychain["lastJWTCall"] == self.getDate()):
                return

        self.clearKeychain()


    def getHttpsResponse(self, p_url, p_path, p_headers = "", p_data = ""):
        url = p_url + p_path
        resp = {"data" : "", "code" : 418}
        # Build a SSL Context to disable certificate verification.
        ctx = ssl._create_unverified_context()

        try:
            if (p_headers == ""):
                request = urllib2.Request(url)
            elif (p_headers != "" and p_data == ""):
                request = urllib2.Request(url, headers=p_headers)
            else:
                request = urllib2.Request(url, data=p_data, headers=p_headers)

            # Open the URL and read the response.
            response = urllib2.urlopen(request, timeout=3, context=ctx)
            resp = {"data" : response.read(), "code" : response.getcode()}
            if(resp["code"] != 200):
                print("Http status code " + str(resp["code"]) + " while accessing " + response.url())
        except urllib2.HTTPError as e:
            resp["code"] = e.code
            self.DEBUG.add_message("14106 getHttpsResponse: " + str(e))
        except Exception as e:
            self.DEBUG.add_message("14106 getHttpsResponse: " + str(e))

        return resp


    def getStatus(self, endpoint, version, kamareonURL, account_id, VIN, gigyaJWTToken, kamareonAPI):
        # fetch data from kamereon (single vehicle)
        path = '/commerce/v1/accounts/' + account_id + '/kamereon/kca/car-adapter/v' + str(version) + '/cars/' + VIN + '/' + endpoint + '?country=DE'
        headers = { "x-gigya-id_token": gigyaJWTToken, "apikey": kamareonAPI, "Content-type": "application/vnd.api+json" }
        apiResult = self.getHttpsResponse(self.g_kamareonURL, path, headers)

        try:
            apiResult = json.loads(apiResult["data"])
        except Exception as e:
            self.DEBUG.add_message("14106 getStatus: " + str(e))

        return apiResult


    # 1. fetch session from gigya
    def getGigyaCookieValue(self):
        path = '/accounts.login?' + urllib.urlencode({'loginID' : self.g_myRenaultUser,
                                                      'password' : self.g_myRenaultPass,
                                                      'apiKey' : self.g_gigyaAPI})

        try:
            apiResult = self.getHttpsResponse( self.g_gigyaURL, path)
            statusCode = apiResult["code"]
            apiResult = apiResult["data"]
            apiResult = json.loads(apiResult)
    
            if( statusCode == "403"):
                print("Login nicht möglich. Zugangsdaten prüfen.")
    
            else:
                gigyaCookieValue = apiResult["sessionInfo"]["cookieValue"]
                self.g_keychain['gigyaCookieValue'] = gigyaCookieValue
                self.DEBUG.set_value("14106 gigyaCookieValue: ", gigyaCookieValue)

        except Exception as e:
            self.DEBUG.add_message("14106 getGigyaCookieValue (Exception): " + str(e))


    # 2. fetch user data from gigya
    def getGigyaUserDate(self):
        gigyaPersonID = ""
        gigyaGigyaDataCenter = ""

        if "gigyaPersonID" in self.g_keychain:
            gigyaPersonID = self.g_keychain['gigyaPersonID']

        if "gigyaGigyaDataCenter" in self.g_keychain:
            gigyaGigyaDataCenter = self.g_keychain['gigyaGigyaDataCenter']

        if(gigyaPersonID == "" or gigyaGigyaDataCenter == ""):
            path = '/accounts.getAccountInfo?' + urllib.urlencode({'oauth_token' : self.g_keychain['gigyaCookieValue']})

            apiResult = self.getHttpsResponse( self.g_gigyaURL, path)
            apiResult = apiResult["data"]
            apiResult = json.loads(apiResult)

            gigyaPersonID = apiResult["data"]["personId"]
            gigyaGigyaDataCenter = apiResult["data"]["gigyaDataCenter"]
            self.g_keychain['gigyaPersonID'] = gigyaPersonID
            self.g_keychain['gigyaGigyaDataCenter'] = gigyaGigyaDataCenter
            self.DEBUG.set_value("14106 gigyaPersonID", gigyaPersonID)
            self.DEBUG.set_value("14106 gigyaGigyaDataCenter", gigyaGigyaDataCenter)


    # 3. fetch JWT data from gigya
    # renew gigyaJWTToken once a day
    def fetchJwtData(self):
        if 'lastJWTCall' not in self.g_keychain:
            self.g_keychain['lastJWTCall'] = 'never'

        gigyaJWTToken = ""
        
        if 'gigyaJWTToken' in self.g_keychain:
            gigyaJWTToken = self.g_keychain['gigyaJWTToken']

        if(gigyaJWTToken == ""):
            expiration = 87000
            gigyaCookieValue = self.g_keychain["gigyaCookieValue"]
            path = '/accounts.getJWT?' + urllib.urlencode({'oauth_token'  : gigyaCookieValue,
                                                           'login_token' : gigyaCookieValue,
                                                           'expiration' : expiration,
                                                           'fields' : 'data.personId,data.gigyaDataCenter',
                                                           'ApiKey' : self.g_gigyaAPI})

            apiResult = self.getHttpsResponse( self.g_gigyaURL, path)
            apiResult = apiResult["data"]
            apiResult = json.loads(apiResult)
            
            gigyaJWTToken = apiResult["id_token"]
            self.g_keychain['gigyaJWTToken'] = gigyaJWTToken
            self.DEBUG.set_value("14106 gigyaJWTToken", gigyaJWTToken)
            
            callDate = self.getDate()
            self.g_keychain['lastJWTCall'] = callDate
            self.DEBUG.set_value("14106 lastJWTCall", callDate)


    # 4. fetch data from kamereon (person)
    # if not in Keychain (we try to avoid quota limits here)
    def fetchKamereonData(self):
        account_id = ""
        if 'account_id' in self.g_keychain:
            account_id = self.g_keychain['account_id']

        if (account_id == ""):

            if ("gigyaPersonID" not in self.g_keychain or 
                "gigyaJWTToken" not in self.g_keychain):
                return

            gigyaPersonID = self.g_keychain["gigyaPersonID"]
            gigyaJWTToken = self.g_keychain["gigyaJWTToken"]

            if (gigyaPersonID == "" or 
                gigyaJWTToken == ""):
                return

            path = '/commerce/v1/persons/' + gigyaPersonID + '?=DE'

            headers = {"x-gigya-id_token" : gigyaJWTToken, "apikey" : self.g_kamareonAPI}

            apiResult = self.getHttpsResponse(self.g_kamareonURL, path, headers)
            apiResult = apiResult["data"]
            apiResult = json.loads(apiResult)

            if(apiResult["type"] == "FUNCTIONAL"):
                print( apiResult["messages"][0]["message"] + " – Login derzeit nicht möglich. Später nochmal versuchen.")

            else:
                account_id = apiResult["accounts"][0]["accountId"]
                self.g_keychain['account_id'] = account_id
                self.DEBUG.set_value("14106 account_id", account_id)

    # 5. fetch data from kamereon (all vehicles data)
    # we need this only once to get the picture of the car and the VIN!
    def fetchVehicleData(self):
        carPicture = ""
        VIN = ""

        if('carPicture' in self.g_keychain):
            carPicture = self.g_keychain['carPicture']

        if( "VIN" in self.g_keychain):
            VIN = self.g_keychain['VIN']

        if ("account_id" not in self.g_keychain):
            print("fetchVehicleData: account_id missing")
            return

        account_id = self.g_keychain['account_id']
        gigyaJWTToken = self.g_keychain["gigyaJWTToken"]

        if (account_id == ""):
            print("fetchVehicleData: account_id empty")
            return

        if(carPicture == "" or VIN == ""):

            path = '/commerce/v1/accounts/' + account_id + '/vehicles?country=DE'
            headers = {"x-gigya-id_token" : gigyaJWTToken, "apikey" : self.g_kamareonAPI}

            try:
                apiResult = self.getHttpsResponse(self.g_kamareonURL, path, headers)
                apiResult = apiResult["data"]
                apiResult = json.loads(apiResult)

                # set carPicture
                carPicture = apiResult["vehicleLinks"][0]["vehicleDetails"]["assets"][0]["renditions"][0]["url"]
                self.g_keychain['carPicture'] = carPicture
                self.DEBUG.set_value("14106 carPicture", carPicture)

                # set VIN
                VIN = apiResult["vehicleLinks"][0]["vin"]
                self.g_keychain['VIN'] = VIN
                self.DEBUG.set_value("14106 VIN", VIN)

            except Exception as e:
                pass

        # NOW WE CAN READ AND SET EVERYTHING INTO AN OBJECT:
        
        allResults = {};
        
        # real configurator picture of the vehicle
        # old call: let carPicture = allVehicleData.vehicleLinks[0].vehicleDetails.assets[0].renditions[0].url // renditions[0] = large // renditions[1] = small image
        allResults["carPicture"] = carPicture
        self.DEBUG.set_value("14106 carPicture: ", carPicture)
        self._set_output_value(self.PIN_O_S_CARPICTURE, carPicture)

        # batteryStatus
        # version: 2
        # batteryLevel = Num (percentage)
        # plugStatus = bolean (0/1)
        # chargeStatus = bolean (0/1) (?)
        try:
            batteryStatus = self.getStatus('battery-status', 2, self.g_kamareonURL, account_id, VIN, gigyaJWTToken, self.g_kamareonAPI)
            allResults["batteryStatus"] = batteryStatus["data"]
            self._set_output_value(self.PIN_O_N_BATTERYLEVEL, int(batteryStatus["data"]["attributes"]["batteryLevel"]))
            self._set_output_value(self.PIN_O_N_PLUGSTATUS, int(batteryStatus["data"]["attributes"]["plugStatus"]))
            self._set_output_value(self.PIN_O_N_CHARGESTATUS, int(batteryStatus["data"]["attributes"]["chargingStatus"]))
            self._set_output_value(self.PIN_O_N_BATTERYAUTONOMY, int(batteryStatus["data"]["attributes"]["batteryAutonomy"]))
            self._set_output_value(self.PIN_O_N_BATTERYAVAILABLEENERGY, int(batteryStatus["data"]["attributes"]["batteryAvailableEnergy"]))
            self._set_output_value(self.PIN_O_N_BATTERYTEMPERATURE, int(batteryStatus["data"]["attributes"]["batteryTemperature"]))
        except Exception as e:
            self.DEBUG.add_message("14106 batteryStatus: " + str(e))

        # cockpitStatus
        # version: 2
        #  totalMileage = Num (in Kilometres!)
        try:
            cockpitStatus = self.getStatus('cockpit', 2, self.g_kamareonURL, account_id, VIN, gigyaJWTToken, self.g_kamareonAPI)
            allResults["cockpitStatus"] = cockpitStatus["data"]
            self._set_output_value(self.PIN_O_N_TOTALMILEAGE, int(cockpitStatus["data"]["attributes"]["totalMileage"]))
        except Exception as e:
            self.DEBUG.add_message("14106 cockpitStatus: " + str(e))

        # locationStatus
        # version: 1
        # gpsLatitude
        # gpsLongitude
        # LastUpdateTime
        try:
            locationStatus = self.getStatus('location', 1, self.g_kamareonURL, account_id, VIN, gigyaJWTToken, self.g_kamareonAPI)
            allResults["locationStatus"] = locationStatus["data"]
            self._set_output_value(self.PIN_O_N_GPSLATITUDE, int(locationStatus["data"]["attributes"]["gpsLatitude"]))
            self._set_output_value(self.PIN_O_N_GPSLONGITUDE, int(locationStatus["data"]["attributes"]["gpsLongitude"]))
            self._set_output_value(self.PIN_O_S_LASTUPDATETIME, str(locationStatus["data"]["attributes"]["lastUpdateTime"]))
        except Exception as e:
            self.DEBUG.add_message("14106 locationStatus: " + str(e))

        ## chargeSchedule
        ## note: unused at the moment!
        ## version: 1
        #try:
        #    chargeSchedule = self.getStatus('charging-settings', 1, self.g_kamareonURL, account_id, VIN, gigyaJWTToken, self.g_kamareonAPI)
        #    allResults["chargeSchedule"] = chargeSchedule["data"]
        #except Exception as e:
        #    self.DEBUG.add_message("14106 chargeSchedule: " + str(e))

        ## hvacStatus
        ## version: 1
        #try:
        #    hvacStatus = self.getStatus('hvac-status', 1, self.g_kamareonURL, account_id, VIN, gigyaJWTToken, self.g_kamareonAPI)
        #    allResults["hvacStatus"] = hvacStatus["data"]
        #    print('hvacStatus: ' + str(hvacStatus))
        #    #self._set_output_value(self.PIN_O_S_LASTUPDATETIME, str(locationStatus["data"]["attributes"]["lastUpdateTime"]))
        #except Exception as e:
        #    self.DEBUG.add_message("14106 hvacStatus: " + str(e))


    # general function to POST status-values to our vehicle
    def postStatus(self, endpoint, jsondata, version, kamareonURL, account_id, VIN, gigyaJWTToken, kamareonAPI ):
        path = '/commerce/v1/accounts/' + account_id + '/kamereon/kca/car-adapter/v' + str(version) + '/cars/' + VIN + '/actions/' + endpoint + '?country=DE'
        headers = { "x-gigya-id_token": gigyaJWTToken, "apikey": kamareonAPI, "Content-type": "application/vnd.api+json" }
        apiResult = self.getHttpsResponse(kamareonURL, path, headers, jsondata)
        return apiResult


    def query(self, query_action):
        self.clearKeychain()
        self.getAccessData()
        action={}
        
        print("requesting " + query_action)

        if ((self.g_VIN == 0) or
            ("account_id" not in self.g_keychain) or
            ("gigyaJWTToken" not in self.g_keychain)):
            print("Required values not in keychain!")
            return

        VIN = self.g_VIN
        account_id = self.g_keychain['account_id']
        gigyaJWTToken = self.g_keychain["gigyaJWTToken"]

        if( query_action == "start_ac" ):
            temp = int(self._get_input_value(self.PIN_I_N_ACTEMP))
            attr_data = ('{"data":{"type":"HvacStart","attributes":{"action":"start","targetTemperature":"' + str(temp) + '"}}}')
            action = self.postStatus('hvac-start', attr_data, 1, self.g_kamareonURL, account_id, VIN, gigyaJWTToken, self.g_kamareonAPI)
            if(action["code"] == 200):
                self._set_output_value(self.PIN_O_N_ACFEEDBACK, 1)
            else:
                self._set_output_value(self.PIN_O_N_ACFEEDBACK, 0)
        elif( query_action == "stop_ac" ):
            attr_data = ('{"data":{"type":"HvacStart","attributes":{"action":"cancel"}}}')
            action = self.postStatus('hvac-start', attr_data, 1, self.g_kamareonURL, account_id, VIN, gigyaJWTToken, self.g_kamareonAPI)
            if(action["code"] == 200):
                self._set_output_value(self.PIN_O_N_ACFEEDBACK, 1)
            else:
                self._set_output_value(self.PIN_O_N_ACFEEDBACK, 0)
        elif( query_action == "start_charge" ):
            attr_data = ('{"data":{"type":"ChargingStart","attributes":{"action":"start"}}}')
            action = self.postStatus('charging-start', attr_data, 1, self.g_kamareonURL, account_id, VIN, gigyaJWTToken, self.g_kamareonAPI)
        else:
            print("Query command not known")

        if(action["code"] == 200):
            self.DEBUG.add_message("14106 query: " + query_action + " OK")
        else:
            self.DEBUG.add_message("14106 query: " + query_action + " nOK, code was " + str(action["code"]))


    def getAccessData(self):
            self.getGigyaCookieValue()
            self.getGigyaUserDate()
            self.fetchJwtData()
            self.fetchKamereonData()


    def onTimeout(self):
        try:
            self.getAccessData()
            self.fetchVehicleData()
        except:
            pass
        
        nInterval = int(self._get_input_value(self.PIN_I_N_INTERVAL))
        print("nInterval = " + str(nInterval))
        if (nInterval > 0):
            t = threading.Timer(nInterval, self.onTimeout).start()


    def on_init(self):
        self.DEBUG = self.FRAMEWORK.create_debug_section()

        self.g_myRenaultUser = self._get_input_value(self.PIN_I_S_USER)
        self.g_myRenaultPass = self._get_input_value(self.PIN_I_S_PW)
        self.g_VIN = self._get_input_value(self.PIN_I_S_VIN)

        nInterval = int(self._get_input_value(self.PIN_I_N_INTERVAL))
        if (nInterval > 0):
            self.onTimeout()


    def on_input_value(self, index, value):
        if(index == self.PIN_I_N_TRIGGER and value != 0):
            self.onTimeout()

        if(index == self.PIN_I_S_USER):
            self.g_myRenaultUser = value
        if(index == self.PIN_I_S_PW):
            self.g_myRenaultPass = value
        if(index == self.PIN_I_S_VIN):
            self.g_VIN = value

        if(index == self.PIN_I_N_AC):
            if(value == 0):
                self.query("stop_ac")
            else:
                self.query("start_ac")
        if(index == self.PIN_I_N_CHARGE):
            self.query("start_charge")

        if(index == self.PIN_I_N_INTERVAL):
            if (value > 0):
                self.onTimeout()
