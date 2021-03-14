# coding: UTF-8

import unittest
import time

# functional import
import urllib
import urllib2
import ssl
import threading
from datetime import datetime
import json

#########################################################

class hsl20_4:
    LOGGING_NONE = 0

    def __init__(self):
        pass

    class BaseModule:
        debug_output_value = {}  # type: float
        debug_set_remanent = {}  # type: float
        debug_input_value = {}

        def __init__(self, a, b):
            pass

        def _get_framework(self):
            f = hsl20_4.Framework()
            return f

        def _get_logger(self, a, b):
            return 0

        def _get_remanent(self, key):
            return 0

        def _set_remanent(self, key, val):
            self.debug_set_remanent = val

        def _set_output_value(self, pin, value):
            self.debug_output_value[int(pin)] = value
            print "# Out: " + str(value) + " @ pin " + str(pin)

        def _get_input_value(self, pin):
            if pin in self.debug_input_value:
                return self.debug_input_value[pin]
            else:
                return 0

    class Framework:
        def __init__(self):
            pass

        def _run_in_context_thread(self, a):
            pass

        def create_debug_section(self):
            d = hsl20_4.DebugHelper()
            return d

    class DebugHelper:
        def __init__(self):
            pass

        def set_value(self, cap, text):
            print("DEBUG value\t'" + str(cap) + "': " + str(text))

        def add_message(self, msg):
            print("Debug Msg\t" + str(msg))

        def add_exception(self, msg):
            print("EXCEPTION Msg\t" + str(msg))

#########################################################

##!!!!##################################################################################################
#### Own written code can be placed above this commentblock . Do not change or delete commentblock! ####
########################################################################################################
##** Code created by generator - DO NOT CHANGE! **##

class Zoe_14106_14106(hsl20_4.BaseModule):

    def __init__(self, homeserver_context):
        hsl20_4.BaseModule.__init__(self, homeserver_context, "14106_Zoe")
        self.FRAMEWORK = self._get_framework()
        self.LOGGER = self._get_logger(hsl20_4.LOGGING_NONE,())
        self.PIN_I_S_USER=1
        self.PIN_I_S_PW=2
        self.PIN_I_S_VIN=3
        self.PIN_I_N_ZOEMODEL=4
        self.PIN_I_N_INTERVAL=5
        self.PIN_I_N_TRIGGER=6
        self.PIN_I_N_AC=7
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

    ########################################################################################################
    #### Own written code can be placed after this commentblock . Do not change or delete commentblock! ####
    ###################################################################################################!!!##

    # do not edit
    g_kamareonURL = "https://api-wired-prod-1-euw1.wrd-aws.com"  # type: str
    g_kamareonAPI = "Ae9FDWugRxZQAGm3Sxgk7uJn6Q4CGEA2"  # type: str
    g_gigyaURL = "https://accounts.eu1.gigya.com"  # type: str
    g_gigyaAPI = "3_7PLksOyBRkHv126x5WhHb-5pqC1qFR8pQjxSeLB6nhAnPERTUlwnYoznHSxwX668"  # type: str
    # austria: "3__B4KghyeUb0GlpU62ZXKrjSfb7CPzwBS368wioftJUL5qXE0Z_sSy0rX69klXuHy"

    g_keychain = {}

    g_error = False

    def clear_keychain(self):
        self.g_keychain = {}

    def get_date(self):
        now = datetime.now()
        timenow = now.strftime("%Y%m%d-%H")  # shall: "20201028-14" (14 = hour)
        return timenow

    def check_time(self):
        if 'lastJWTCall' in self.g_keychain:
            if self.g_keychain["lastJWTCall"] == self.get_date():
                return True

        self.clear_keychain()
        return False

    def get_https_response(self, p_url, p_path, p_headers="", p_data=""):
        url = p_url + p_path
        resp = {"data": "", "code": 418}
        # Build a SSL Context to disable certificate verification.
        ctx = ssl._create_unverified_context()

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
            self.DEBUG.add_message("Http status code " + str(resp["code"]) + " while accessing " + response.url())

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
                self.DEBUG.add_exception("Error get_status: " + str(e))

            return api_result
        else:
            return {}

    # 1. fetch session from gigya
    def get_gigya_cookie_value(self):
        renault_user = self._get_input_value(self.PIN_I_S_USER)
        renault_pass = self._get_input_value(self.PIN_I_S_PW)
        vin = self._get_input_value(self.PIN_I_S_VIN)

        path = '/accounts.login?' + urllib.urlencode({'loginID': renault_user,
                                                      'password': renault_pass,
                                                      'include': 'data',
                                                      'apiKey': self.g_gigyaAPI})
        try:
            api_result = self.get_https_response(self.g_gigyaURL, path)
            status_code = api_result["code"]
            api_result = api_result["data"]
            api_result = json.loads(api_result)

        except Exception as e:
            self.DEBUG.add_exception("Error get_gigya_cookie_value http response: " + str(e.message))
            status_code = 999
            api_result = {}

        print("1. get_gigya_cookie_value, status code: " + str(status_code))

        if int(status_code) != 200:
            self.DEBUG.add_message(api_result["errorMessage"])

        else:
            try:
                gigya_cookie_value = api_result["sessionInfo"]["cookieValue"]
                self.g_keychain['gigyaCookieValue'] = gigya_cookie_value
                self.DEBUG.add_message("Received gigyaCookieValue")

                api_result = api_result['data']
                person_id = api_result["personId"]
                self.g_keychain['gigyaPersonID'] = person_id
                self.DEBUG.add_message("Received gigyaPersonId")

                gigya_data_center = api_result['gigyaDataCenter']
                self.g_keychain['gigyaDataCenter'] = gigya_data_center
                self.DEBUG.add_message("Received gigyaDataCenter")

            except Exception as e:
                self.DEBUG.add_exception("Error getGigyaCookieValue: " + str(e.message))

    # 2. fetch user data from gigya
    def get_gigya_user_date(self):
        gigya_person_id = ""
        gigya_gigya_data_center = ""

        if "gigyaPersonID" in self.g_keychain:
            gigya_person_id = self.g_keychain['gigyaPersonID']

        if "gigyaDataCenter" in self.g_keychain:
            gigya_gigya_data_center = self.g_keychain['gigyaDataCenter']

        if gigya_person_id == "" or gigya_gigya_data_center == "":
            path = '/accounts.getAccountInfo?' + urllib.urlencode({'oauth_token': self.g_keychain['gigyaCookieValue']})
            api_result = self.get_https_response(self.g_gigyaURL, path)
            api_result = api_result["data"]
            api_result = json.loads(api_result)
            status_code = api_result["statusCode"]

            print("2. get_gigya_user_date, status code: " + str(status_code))

            gigya_person_id = api_result["data"]["personId"]
            gigya_gigya_data_center = api_result["data"]["gigyaDataCenter"]
            self.g_keychain['gigyaPersonID'] = gigya_person_id
            self.g_keychain['gigyaDataCenter'] = gigya_gigya_data_center
            self.DEBUG.add_message("Received gigyaPersonID")
            self.DEBUG.add_message("Received gigyaDataCenter")

        else:
            print("2. get_gigya_user_date, no action required")

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
            api_result = api_result["data"]
            api_result = json.loads(api_result)
            status_code = api_result["statusCode"]
            print("3. fetch_jwt_data, status code: " + str(status_code))

            gigya_jwt_token = api_result["id_token"]
            self.g_keychain['gigyaJWTToken'] = gigya_jwt_token
            self.DEBUG.add_message("Received gigyaJWTToken")

            call_date = self.get_date()
            self.g_keychain['lastJWTCall'] = call_date
            self.DEBUG.add_message("Set lastJWTCall")

        else:
            print("3. fetch_jwt_data, no action required")

    # 4. fetch data from kamereon (person)
    # if not in Keychain (we try to avoid quota limits here)
    def fetch_kamereon_data(self):
        account_id = ""
        if 'account_id' in self.g_keychain:
            account_id = self.g_keychain['account_id']

        if account_id == "":

            if ("gigyaPersonID" not in self.g_keychain or
                    "gigyaJWTToken" not in self.g_keychain):
                self.DEBUG.add_message("fetch_kamereon_data: Missing items in keychain, aborting.")
                return

            gigya_person_id = self.g_keychain["gigyaPersonID"]
            gigya_jwt_token = self.g_keychain["gigyaJWTToken"]

            if (gigya_person_id == "" or
                    gigya_jwt_token == ""):
                self.DEBUG.add_message("fetch_kamereon_data: Missing items in keychain, aborting.")
                return

            path = '/commerce/v1/persons/' + gigya_person_id + '?=DE'
            headers = {"x-gigya-id_token": gigya_jwt_token, "apikey": self.g_kamareonAPI}

            api_result = self.get_https_response(self.g_kamareonURL, path, headers)
            status_code = api_result["code"]
            api_result = api_result["data"]
            api_result = json.loads(api_result)
            print("4. fetch_kamereon_data, status code: " + str(status_code))

            if api_result["type"] == "FUNCTIONAL":
                self.DEBUG.add_message(api_result["messages"][0]["message"] + " – Login derzeit nicht möglich. Später nochmal versuchen.")

            else:
                account_id = api_result["accounts"][0]["accountId"]
                self.g_keychain['account_id'] = account_id
                self.DEBUG.add_message("Received account_id")

    # 5. fetch data from kamereon (all vehicles data)
    # we need this only once to get the picture of the car and the VIN!
    def fetch_vehicle_data(self):
        car_picture = ""
        vin = ""
        gigya_jwt_token = ""

        if 'carPicture' in self.g_keychain:
            car_picture = self.g_keychain['carPicture']

        if "vin" in self.g_keychain:
            vin = self.g_keychain['vin']

        if "account_id" not in self.g_keychain:
            self.DEBUG.add_message("fetchVehicleData: account_id empty")
            return

        account_id = self.g_keychain['account_id']

        if account_id == "":
            self.DEBUG.add_message("fetchVehicleData: account_id empty")
            return

        if "gigyaJWTToken" not in self.g_keychain:
            self.DEBUG.add_message("fetchVehicleData: gigyaJWTToken empty")
            return

        gigya_jwt_token = self.g_keychain["gigyaJWTToken"]

        if gigya_jwt_token == "":
            self.DEBUG.add_message("fetchVehicleData: gigyaJWTToken empty")
            return

        if car_picture == "" or vin == "":
            path = '/commerce/v1/accounts/' + account_id + '/vehicles?country=DE'
            headers = {"x-gigya-id_token": gigya_jwt_token, "apikey": self.g_kamareonAPI}

            try:
                api_result = self.get_https_response(self.g_kamareonURL, path, headers)
                api_result = api_result["data"]
                api_result = json.loads(api_result)

                # set carPicture
                car_picture = api_result["vehicleLinks"][0]["vehicleDetails"]["assets"][0]["renditions"][0]["url"]
                self.g_keychain['carPicture'] = car_picture
                self.DEBUG.add_message("Received carPicture")

                # set vin
                vin = api_result["vehicleLinks"][0]["vin"]
                self.g_keychain['vin'] = vin
                self.DEBUG.add_message("Received vin")

            except Exception as e:
                self.DEBUG.add_exception("Exception in vehicleLinks")
                self.g_error = True

        # NOW WE CAN READ AND SET EVERYTHING INTO AN OBJECT:

        all_results = {"carPicture": car_picture}

        # real configurator picture of the vehicle
        self._set_output_value(self.PIN_O_S_CARPICTURE, car_picture)

        # batteryStatus
        # version: 2
        # batteryLevel = Num (percentage)
        # plugStatus = bolean (0/1)
        # chargeStatus = bolean (0/1) (?)
        try:
            print("+++")
            print(self.g_kamareonURL + "; " + account_id + "; " + vin + "; " + gigya_jwt_token + "; " + self.g_kamareonAPI)
            print("+++")
            battery_status = self.get_status('battery-status', 2, self.g_kamareonURL, account_id, vin, gigya_jwt_token,
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
            self.DEBUG.add_exception("Error batteryStatus: " + str(e))
            self.g_error = True

        # cockpitStatus
        # version: 2
        #  totalMileage = Num (in Kilometres!)
        try:
            cockpit_status = self.get_status('cockpit', 2, self.g_kamareonURL, account_id, vin, gigya_jwt_token,
                                             self.g_kamareonAPI)
            all_results["cockpitStatus"] = cockpit_status["data"]
            self._set_output_value(self.PIN_O_N_TOTALMILEAGE, int(cockpit_status["data"]["attributes"]["totalMileage"]))
        except Exception as e:
            self.DEBUG.add_exception("Error cockpitStatus: " + str(e))
            self.g_error = True

        # locationStatus
        # version: 1
        # gpsLatitude
        # gpsLongitude
        # LastUpdateTime
        try:
            location_status = self.get_status('location', 1, self.g_kamareonURL, account_id, vin, gigya_jwt_token,
                                              self.g_kamareonAPI)
            all_results["locationStatus"] = location_status["data"]
            self._set_output_value(self.PIN_O_N_GPSLATITUDE, int(location_status["data"]["attributes"]["gpsLatitude"]))
            self._set_output_value(self.PIN_O_N_GPSLONGITUDE,
                                   int(location_status["data"]["attributes"]["gpsLongitude"]))
            self._set_output_value(self.PIN_O_S_LASTUPDATETIME,
                                   str(location_status["data"]["attributes"]["lastUpdateTime"]))
        except Exception as e:
            self.DEBUG.add_exception("Error locationStatus: " + str(e))
            self.g_error = True

        # chargeSchedule
        # note: unused at the moment!
        # version: 1
        # try:
        #    chargeSchedule = self.getStatus('charging-settings', 1, self.g_kamareonURL, account_id, vin, gigyaJWTToken,
        #                                   self.g_kamareonAPI)
        #    allResults["chargeSchedule"] = chargeSchedule["data"]
        # except Exception as e:
        #    self.DEBUG.add_message("14106 chargeSchedule: " + str(e))

        # hvacStatus
        # version: 1
        # try:
        #    hvac_status = self.get_status('hvac-status', 1, self.g_kamareonURL, account_id, vin, gigya_jwt_token,
        #                                 self.g_kamareonAPI)
        #    if "data" in hvac_status:
        #        all_results["hvacStatus"] = hvac_status["data"]
        #        print('hvacStatus: ' + str(hvac_status))
        # except Exception as e:
        #    self.DEBUG.add_message("14106 hvacStatus: " + str(e))
        #    self.g_error = True

    # general function to POST status-values to our vehicle
    def post_status(self, endpoint, jsondata, version, kamareonURL, account_id, vin, gigyaJWTToken, kamareonAPI):

        path = '/commerce/v1/accounts/' + account_id + '/kamereon/kca/car-adapter/v' + str(
            version) + '/cars/' + vin + '/actions/' + endpoint + '?country=DE'
        headers = {"x-gigya-id_token": gigyaJWTToken, "apikey": kamareonAPI, "Content-type": "application/vnd.api+json"}
        api_result = self.get_https_response(kamareonURL, path, headers, jsondata)
        return api_result

    def reset_ac_feedback(self):
        self._set_output_value(self.PIN_O_N_ACFEEDBACK, 0)

    def query(self, query_action):
        self.clear_keychain()
        self.get_access_data()
        action = {}
        vin = self._get_input_value(self.PIN_I_S_VIN)

        print("requesting " + query_action)

        if ((vin == 0) or
                ("account_id" not in self.g_keychain) or
                ("gigyaJWTToken" not in self.g_keychain)):
            print("Required values not in keychain!")
            return

        account_id = self.g_keychain['account_id']
        gigya_jwt_token = self.g_keychain["gigyaJWTToken"]

        if query_action == "start_ac":
            attr_data = '{"data":{"type":"HvacStart","attributes":{"action":"start","targetTemperature":"21"}}}'
            self._set_output_value(self.PIN_O_N_ACFEEDBACK, 1)
            action = self.post_status('hvac-start', attr_data, 1, self.g_kamareonURL, account_id, vin, gigya_jwt_token,
                                      self.g_kamareonAPI)
            if action["code"] == 200:
                self._set_output_value(self.PIN_O_N_ACFEEDBACK, 2)
                threading.Timer(300, self.reset_ac_feedback).start()

        elif query_action == "stop_ac":
            attr_data = '{"data":{"type":"HvacStart","attributes":{"action":"cancel"}}}'
            action = self.post_status('hvac-start', attr_data, 1, self.g_kamareonURL, account_id, vin, gigya_jwt_token,
                                      self.g_kamareonAPI)
        elif query_action == "start_charge":
            attr_data = '{"data":{"type":"ChargingStart","attributes":{"action":"start"}}}'
            action = self.post_status('charging-start', attr_data, 1, self.g_kamareonURL, account_id, vin, gigya_jwt_token,
                                      self.g_kamareonAPI)
        else:
            self.DEBUG.add_message("Query command '" + str(query_action) + "' not known")

        if action["code"] == 200:
            self.DEBUG.add_message("hvacStatus: " + query_action + " OK")
        else:
            self.DEBUG.add_message("hvacStatus: " + query_action + " nOK, code was " + str(action["code"]))

    def get_access_data(self):
        self.get_gigya_cookie_value()
        self.get_gigya_user_date()
        self.fetch_jwt_data()
        self.fetch_kamereon_data()

    def on_timeout(self):
        self.DEBUG.add_message("Requesting vehicle data.")
        try:
            if not self.check_time():
                self.get_access_data()
            else:
                print("Access data still valid! Skipping get_access_data().")
            self.fetch_vehicle_data()
        except Exception as e:
            self.DEBUG.add_exception("Error on_timeout: " + str(e))

        interval = int(self._get_input_value(self.PIN_I_N_INTERVAL))
        if interval > 0:
            threading.Timer(interval, self.on_timeout).start()

    def on_init(self):
        self.DEBUG = self.FRAMEWORK.create_debug_section()

        # do not edit
        self.g_kamareonURL = "https://api-wired-prod-1-euw1.wrd-aws.com"  # type: str
        self.g_kamareonAPI = "Ae9FDWugRxZQAGm3Sxgk7uJn6Q4CGEA2"  # type: str
        self.g_gigyaURL = "https://accounts.eu1.gigya.com"  # type: str
        self.g_gigyaAPI = "3_7PLksOyBRkHv126x5WhHb-5pqC1qFR8pQjxSeLB6nhAnPERTUlwnYoznHSxwX668"  # type: str
        # austria: "3__B4KghyeUb0GlpU62ZXKrjSfb7CPzwBS368wioftJUL5qXE0Z_sSy0rX69klXuHy"

        self.g_keychain = {}

        self.g_error = False

        interval = int(self._get_input_value(self.PIN_I_N_INTERVAL))
        if interval > 0:
            self.on_timeout()

    def on_input_value(self, index, value):
        if index == self.PIN_I_N_TRIGGER and value:
            self.on_timeout()

        elif index == self.PIN_I_N_AC:
            if value == 0:
                self.query("stop_ac")
            else:
                self.query("start_ac")
        elif index == self.PIN_I_N_CHARGE:
            self.query("start_charge")
        elif index == self.PIN_I_N_INTERVAL:
            if value > 0:
                self.on_timeout()


################################################################################


class TestSequenceFunctions(unittest.TestCase):

    tst = Zoe_14106_14106(0)

    def setUp(self):
        print("\n###setUp")
        with open("credentials.txt") as f:
            self.cred = json.load(f)

        self.tst = Zoe_14106_14106(0)
        self.tst.on_init()

        self.tst.debug_input_value[self.tst.PIN_I_S_PW] = self.cred["PIN_I_S_PW"]
        self.tst.debug_input_value[self.tst.PIN_I_S_USER] = self.cred["PIN_I_S_USER"]
        self.tst.debug_input_value[self.tst.PIN_I_S_VIN] = self.cred["PIN_I_S_VIN"]

    def test_redo(self):
        print("### redo")
        self.tst.on_input_value(self.tst.PIN_I_N_TRIGGER, 1)
        time.sleep(5)
        self.tst.on_input_value(self.tst.PIN_I_N_TRIGGER, 1)
        self.assertFalse(self.tst.g_error)

    def test_clear_keychain(self):
        print("### test_clear_keychain")
        self.tst.g_keychain = {'lastJWTCall': '20210311-20', 'account_id': '00000000-0000-0000-0000-00000000000',
                               'vin': '00000000000000000', 'gigyaJWTToken': 'eyJ0eXAiOi',
                               'gigyaPersonID': '0000', 'carPicture': 'https://...',
                               'gigyaDataCenter': 'eu1.gigya.com', 'gigyaCookieValue': '...'}

        self.assertNotEqual(0, len(self.tst.g_keychain), "a")
        self.tst.clear_keychain()
        self.assertEqual(0, len(self.tst.g_keychain), "b")

    def test_no_route(self):
        print("### test_no_route")
        self.tst.g_gigyaURL = "192.168.1.100"
        self.tst.on_input_value(self.tst.PIN_I_N_TRIGGER, 1)

if __name__ == '__main__':
    unittest.main()
