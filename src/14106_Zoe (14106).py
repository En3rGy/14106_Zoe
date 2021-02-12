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
    g_kamareonURL = "https://api-wired-prod-1-euw1.wrd-aws.com"  # type: str
    g_kamareonAPI = "Ae9FDWugRxZQAGm3Sxgk7uJn6Q4CGEA2"  # type: str
    g_gigyaURL = "https://accounts.eu1.gigya.com"  # type: str
    g_gigyaAPI = "3_7PLksOyBRkHv126x5WhHb-5pqC1qFR8pQjxSeLB6nhAnPERTUlwnYoznHSxwX668"  # type: str
    # austria: "3__B4KghyeUb0GlpU62ZXKrjSfb7CPzwBS368wioftJUL5qXE0Z_sSy0rX69klXuHy"

    g_keychain = {}

    def clear_keychain(self):
        if 'account_id' in self.g_keychain:
            del self.g_keychain['account_id']
        if 'gigyaJWTToken' in self.g_keychain:
            del self.g_keychain['gigyaJWTToken']
        if 'gigyaCookieValue' in self.g_keychain:
            del self.g_keychain['gigyaCookieValue']
        if 'gigyaPersonID' in self.g_keychain:
            del self.g_keychain['gigyaPersonID']
        if 'gigyaDataCenter' in self.g_keychain:
            del self.g_keychain['gigyaDataCenter']

    def get_date(self):
        now = datetime.now()
        timenow = now.strftime("%Y%m%d-%H")  # shall: "20201028-14" (14 = hour)
        return timenow

    def check_time(self):
        if 'lastJWTCall' in self.g_keychain:
            if self.g_keychain["lastJWTCall"] == self.get_date():
                return

        self.clear_keychain()

    def get_https_response(self, p_url, p_path, p_headers="", p_data=""):
        url = p_url + p_path
        resp = {"data": "", "code": 418}
        # Build a SSL Context to disable certificate verification.
        ctx = ssl._create_unverified_context()

        try:
            if p_headers == "":
                request = urllib2.Request(url)
            elif p_headers != "" and p_data == "":
                request = urllib2.Request(url, headers=p_headers)
            else:
                request = urllib2.Request(url, data=p_data, headers=p_headers)

            # Open the URL and read the response.
            response = urllib2.urlopen(request, timeout=3, context=ctx)
            resp = {"data": response.read(), "code": response.getcode()}
            if resp["code"] != 200:
                print("Http status code " + str(resp["code"]) + " while accessing " + response.url())
        except urllib2.HTTPError as e:
            resp["code"] = e.code
            self.DEBUG.add_message("14106 getHttpsResponse: (urllib2) " + str(e))
        except Exception as e:
            self.DEBUG.add_message("14106 getHttpsResponse: " + str(e))

        return resp

    def get_status(self, endpoint, version, kamareonURL, account_id, VIN, gigyaJWTToken, kamareonAPI):
        # fetch data from kamereon (single vehicle)
        path = '/commerce/v1/accounts/' + account_id + '/kamereon/kca/car-adapter/v' + str(
            version) + '/cars/' + VIN + '/' + endpoint + '?country=DE'
        headers = {"x-gigya-id_token": gigyaJWTToken, "apikey": kamareonAPI, "Content-type": "application/vnd.api+json"}
        api_result = self.get_https_response(self.g_kamareonURL, path, headers)
        status_code = api_result["code"]
        api_result = api_result["data"]

        print("x. " + endpoint + " status: " + str(status_code))

        if status_code == 200:
            try:
                api_result = json.loads(api_result)
            except Exception as e:
                self.DEBUG.add_message("14106 get_status: " + str(e))

            return api_result
        else:
            return {}

    # 1. fetch session from gigya
    def get_gigya_cookie_value(self):
        path = '/accounts.login?' + urllib.urlencode({'loginID': self.g_myRenaultUser,
                                                      'password': self.g_myRenaultPass,
                                                      'include': 'data',
                                                      'apiKey': self.g_gigyaAPI})
        try:
            api_result = self.get_https_response(self.g_gigyaURL, path)
            status_code = api_result["code"]
            api_result = api_result["data"]
            api_result = json.loads(api_result)

            print("1. status code: " + str(status_code))

            if status_code == "403":
                print("Login nicht möglich. Zugangsdaten prüfen.")
            else:
                gigya_cookie_value = api_result["sessionInfo"]["cookieValue"]
                self.g_keychain['gigyaCookieValue'] = gigya_cookie_value
                self.DEBUG.set_value("14106 gigyaCookieValue: ", gigya_cookie_value)

                api_result = api_result['data']
                person_id = api_result["personId"]
                self.g_keychain['gigyaPersonID'] = person_id
                self.DEBUG.set_value("14106 gigyaPersonId: ", person_id)

                gigya_data_center = api_result['gigyaDataCenter']
                self.g_keychain['gigyaDataCenter'] = gigya_data_center
                self.DEBUG.set_value("14106 gigyaDataCenter: ", gigya_data_center)

        except Exception as e:
            self.DEBUG.add_message("14106 getGigyaCookieValue (Exception): " + str(e))

    # 2. fetch user data from gigya
    def get_gigya_user_date(self):
        gigya_person_id = ""
        gigya_gigya_data_center = ""

        if "gigyaPersonID" in self.g_keychain:
            gigya_person_id = self.g_keychain['gigyaPersonID']

        if "gigyaDataCenter" in self.g_keychain:
            gigya_gigya_data_center = self.g_keychain['gigyaDataCenter']

        if gigya_person_id == "" or gigya_gigya_data_center == "":
            print ("a")
            path = '/accounts.getAccountInfo?' + urllib.urlencode({'oauth_token': self.g_keychain['gigyaCookieValue']})
            api_result = self.get_https_response(self.g_gigyaURL, path)
            status_code = api_result["code"]
            api_result = api_result["data"]
            api_result = json.loads(api_result)

            print("2. status code: " + str(status_code))

            gigya_person_id = api_result["data"]["personId"]
            gigya_gigya_data_center = api_result["data"]["gigyaDataCenter"]
            self.g_keychain['gigyaPersonID'] = gigya_person_id
            self.g_keychain['gigyaDataCenter'] = gigya_gigya_data_center
            self.DEBUG.set_value("14106 gigyaPersonID", self.g_keychain['gigyaPersonID'])
            self.DEBUG.set_value("14106 gigyaDataCenter", self.g_keychain['gigyaDataCenter'])

        else:
            print("2. no action required")

    # 3. fetch JWT data from gigya
    # renew gigyaJWTToken once a day
    def fetch_jwt_data(self):
        if 'lastJWTCall' not in self.g_keychain:
            self.g_keychain['lastJWTCall'] = 'never'

        gigya_jwt_token = ""

        if 'gigyaJWTToken' in self.g_keychain:
            gigya_jwt_token = self.g_keychain['gigyaJWTToken']

        if gigya_jwt_token == "":
            expiration = 87000
            gigya_cookie_value = self.g_keychain["gigyaCookieValue"]
            path = '/accounts.getJWT?' + urllib.urlencode({'oauth_token': gigya_cookie_value,
                                                           'login_token': gigya_cookie_value,
                                                           'expiration': expiration,
                                                           'fields': 'data.personId,data.gigyaDataCenter',
                                                           'ApiKey': self.g_gigyaAPI})

            api_result = self.get_https_response(self.g_gigyaURL, path)
            status_code = api_result["code"]
            api_result = api_result["data"]
            print("3. status code: " + str(status_code))
            api_result = json.loads(api_result)

            gigya_jwt_token = api_result["id_token"]
            self.g_keychain['gigyaJWTToken'] = gigya_jwt_token

            call_date = self.get_date()
            self.g_keychain['lastJWTCall'] = call_date

        else:
            print("3. no action required")

        self.DEBUG.set_value("14106 gigyaJWTToken", self.g_keychain['gigyaJWTToken'])
        self.DEBUG.set_value("14106 lastJWTCall", self.g_keychain['lastJWTCall'])

    # 4. fetch data from kamereon (person)
    # if not in Keychain (we try to avoid quota limits here)
    def fetch_kamereon_data(self):
        account_id = ""
        if 'account_id' in self.g_keychain:
            account_id = self.g_keychain['account_id']

        if account_id == "":

            if ("gigyaPersonID" not in self.g_keychain or
                    "gigyaJWTToken" not in self.g_keychain):
                self.DEBUG.add_message("14106 fetch_kamereon_data: Missing items in keychain, aborting.")
                return

            gigya_person_id = self.g_keychain["gigyaPersonID"]
            gigya_jwt_token = self.g_keychain["gigyaJWTToken"]

            if (gigya_person_id == "" or
                    gigya_jwt_token == ""):
                self.DEBUG.add_message("14106 fetch_kamereon_data: Missing items in keychain, aborting.")
                return

            path = '/commerce/v1/persons/' + gigya_person_id + '?=DE'
            headers = {"x-gigya-id_token": gigya_jwt_token, "apikey": self.g_kamareonAPI}

            api_result = self.get_https_response(self.g_kamareonURL, path, headers)
            status_code = api_result["code"]
            api_result = api_result["data"]
            api_result = json.loads(api_result)
            print("4. status code: " + str(status_code))

            if api_result["type"] == "FUNCTIONAL":
                print(api_result["messages"][0][
                          "message"] + " – Login derzeit nicht möglich. Später nochmal versuchen.")

            else:
                account_id = api_result["accounts"][0]["accountId"]
                self.g_keychain['account_id'] = account_id
                self.DEBUG.set_value("14106 account_id", account_id)

    # 5. fetch data from kamereon (all vehicles data)
    # we need this only once to get the picture of the car and the VIN!
    def fetch_vehicle_data(self):
        car_picture = ""
        VIN = ""
        gigya_jwt_token = ""

        if 'carPicture' in self.g_keychain:
            car_picture = self.g_keychain['carPicture']

        if "VIN" in self.g_keychain:
            VIN = self.g_keychain['VIN']

        if "account_id" not in self.g_keychain:
            print("fetchVehicleData: account_id missing")
            return

        account_id = self.g_keychain['account_id']

        if account_id == "":
            print("fetchVehicleData: account_id empty")
            return

        if car_picture == "" or VIN == "":
            gigya_jwt_token = self.g_keychain["gigyaJWTToken"]

            path = '/commerce/v1/accounts/' + account_id + '/vehicles?country=DE'
            headers = {"x-gigya-id_token": gigya_jwt_token, "apikey": self.g_kamareonAPI}

            try:
                api_result = self.get_https_response(self.g_kamareonURL, path, headers)
                api_result = api_result["data"]
                api_result = json.loads(api_result)

                # set carPicture
                car_picture = api_result["vehicleLinks"][0]["vehicleDetails"]["assets"][0]["renditions"][0]["url"]
                self.g_keychain['carPicture'] = car_picture
                self.DEBUG.set_value("14106 carPicture", car_picture)

                # set VIN
                VIN = api_result["vehicleLinks"][0]["vin"]
                self.g_keychain['VIN'] = VIN
                self.DEBUG.set_value("14106 VIN", VIN)

            except Exception as e:
                print("Exception in vehicleLinks")

        # NOW WE CAN READ AND SET EVERYTHING INTO AN OBJECT:

        all_results = {}

        # real configurator picture of the vehicle
        # old call: let carPicture = allVehicleData.vehicleLinks[0].vehicleDetails.assets[0].renditions[0].url // renditions[0] = large // renditions[1] = small image
        all_results["carPicture"] = car_picture
        self.DEBUG.set_value("14106 carPicture: ", car_picture)
        self._set_output_value(self.PIN_O_S_CARPICTURE, car_picture)

        # batteryStatus
        # version: 2
        # batteryLevel = Num (percentage)
        # plugStatus = bolean (0/1)
        # chargeStatus = bolean (0/1) (?)
        try:
            battery_status = self.get_status('battery-status', 2, self.g_kamareonURL, account_id, VIN, gigya_jwt_token,
                                             self.g_kamareonAPI)
            all_results["batteryStatus"] = battery_status["data"]
            self._set_output_value(self.PIN_O_N_BATTERYLEVEL, int(battery_status["data"]["attributes"]["batteryLevel"]))
            self._set_output_value(self.PIN_O_N_PLUGSTATUS, int(battery_status["data"]["attributes"]["plugStatus"]))
            self._set_output_value(self.PIN_O_N_CHARGESTATUS,
                                   int(battery_status["data"]["attributes"]["chargingStatus"]))
            self._set_output_value(self.PIN_O_N_BATTERYAUTONOMY,
                                   int(battery_status["data"]["attributes"]["batteryAutonomy"]))
            self._set_output_value(self.PIN_O_N_BATTERYAVAILABLEENERGY,
                                   int(battery_status["data"]["attributes"]["batteryAvailableEnergy"]))
            self._set_output_value(self.PIN_O_N_BATTERYTEMPERATURE,
                                   int(battery_status["data"]["attributes"]["batteryTemperature"]))
        except Exception as e:
            self.DEBUG.add_message("14106 batteryStatus: " + str(e))

        # cockpitStatus
        # version: 2
        #  totalMileage = Num (in Kilometres!)
        try:
            cockpit_status = self.get_status('cockpit', 2, self.g_kamareonURL, account_id, VIN, gigya_jwt_token,
                                             self.g_kamareonAPI)
            all_results["cockpitStatus"] = cockpit_status["data"]
            self._set_output_value(self.PIN_O_N_TOTALMILEAGE, int(cockpit_status["data"]["attributes"]["totalMileage"]))
        except Exception as e:
            self.DEBUG.add_message("14106 cockpitStatus: " + str(e))

        # locationStatus
        # version: 1
        # gpsLatitude
        # gpsLongitude
        # LastUpdateTime
        try:
            location_status = self.get_status('location', 1, self.g_kamareonURL, account_id, VIN, gigya_jwt_token,
                                              self.g_kamareonAPI)
            all_results["locationStatus"] = location_status["data"]
            self._set_output_value(self.PIN_O_N_GPSLATITUDE, int(location_status["data"]["attributes"]["gpsLatitude"]))
            self._set_output_value(self.PIN_O_N_GPSLONGITUDE,
                                   int(location_status["data"]["attributes"]["gpsLongitude"]))
            self._set_output_value(self.PIN_O_S_LASTUPDATETIME,
                                   str(location_status["data"]["attributes"]["lastUpdateTime"]))
        except Exception as e:
            self.DEBUG.add_message("14106 locationStatus: " + str(e))

        # chargeSchedule
        # note: unused at the moment!
        # version: 1
        # try:
        #    chargeSchedule = self.getStatus('charging-settings', 1, self.g_kamareonURL, account_id, VIN, gigyaJWTToken,
        #                                   self.g_kamareonAPI)
        #    allResults["chargeSchedule"] = chargeSchedule["data"]
        # except Exception as e:
        #    self.DEBUG.add_message("14106 chargeSchedule: " + str(e))

        # hvacStatus
        # version: 1
        try:
            hvac_status = self.get_status('hvac-status', 1, self.g_kamareonURL, account_id, VIN, gigya_jwt_token,
                                         self.g_kamareonAPI)
            if "data" in hvac_status:
                all_results["hvacStatus"] = hvac_status["data"]
                print('hvacStatus: ' + str(hvac_status))
        except Exception as e:
            self.DEBUG.add_message("14106 hvacStatus: " + str(e))

    # general function to POST status-values to our vehicle
    def post_status(self, endpoint, jsondata, version, kamareonURL, account_id, VIN, gigyaJWTToken, kamareonAPI):
        path = '/commerce/v1/accounts/' + account_id + '/kamereon/kca/car-adapter/v' + str(
            version) + '/cars/' + VIN + '/actions/' + endpoint + '?country=DE'
        headers = {"x-gigya-id_token": gigyaJWTToken, "apikey": kamareonAPI, "Content-type": "application/vnd.api+json"}
        api_result = self.get_https_response(kamareonURL, path, headers, jsondata)
        return api_result

    def query(self, query_action):
        self.clear_keychain()
        self.get_access_data()
        action = {}

        print("requesting " + query_action)

        if ((self.g_VIN == 0) or
                ("account_id" not in self.g_keychain) or
                ("gigyaJWTToken" not in self.g_keychain)):
            print("Required values not in keychain!")
            return

        VIN = self.g_VIN
        account_id = self.g_keychain['account_id']
        gigya_jwt_token = self.g_keychain["gigyaJWTToken"]

        if query_action == "start_ac":
            attr_data = '{"data":{"type":"HvacStart","attributes":{"action":"start","targetTemperature":"21"}}}'
            action = self.post_status('hvac-start', attr_data, 1, self.g_kamareonURL, account_id, VIN, gigya_jwt_token,
                                      self.g_kamareonAPI)
        elif query_action == "stop_ac":
            attr_data = '{"data":{"type":"HvacStart","attributes":{"action":"cancel"}}}'
            action = self.post_status('hvac-start', attr_data, 1, self.g_kamareonURL, account_id, VIN, gigya_jwt_token,
                                      self.g_kamareonAPI)
        elif query_action == "start_charge":
            attr_data = '{"data":{"type":"ChargingStart","attributes":{"action":"start"}}}'
            action = self.post_status('charging-start', attr_data, 1, self.g_kamareonURL, account_id, VIN, gigya_jwt_token,
                                      self.g_kamareonAPI)
        else:
            print("Query command not known")

        if action["code"] == 200:
            self.DEBUG.add_message("14106 hvacStatus: " + query_action + " OK")
        else:
            self.DEBUG.add_message("14106 hvacStatus: " + query_action + " nOK, code was " + str(action["code"]))

    def get_access_data(self):
        self.get_gigya_cookie_value()
        self.get_gigya_user_date()
        self.fetch_jwt_data()
        self.fetch_kamereon_data()

    def on_timeout(self):
        try:
            self.get_access_data()
            self.fetch_vehicle_data()
        except Exception as e:
            print("14106 on_timeout: " + str(e))


        interval = int(self._get_input_value(self.PIN_I_N_INTERVAL))
        if interval > 0:
            t = threading.Timer(interval, self.on_timeout).start()

    def on_init(self):
        self.DEBUG = self.FRAMEWORK.create_debug_section()

        self.g_myRenaultUser = self._get_input_value(self.PIN_I_S_USER)
        self.g_myRenaultPass = self._get_input_value(self.PIN_I_S_PW)
        self.g_VIN = self._get_input_value(self.PIN_I_S_VIN)

        interval = int(self._get_input_value(self.PIN_I_N_INTERVAL))
        if interval > 0:
            self.on_timeout()

    def on_input_value(self, index, value):
        if index == self.PIN_I_N_TRIGGER and value:
            self.on_timeout()

        if index == self.PIN_I_S_USER:
            self.g_myRenaultUser = value
        if index == self.PIN_I_S_PW:
            self.g_myRenaultPass = value
        if index == self.PIN_I_S_VIN:
            self.g_VIN = value

        if index == self.PIN_I_N_INTERVAL:
            if value > 0:
                self.on_timeout()
