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

################################
# get the code
with open('framework_helper.py', 'r') as f1, open('../src/14106_Zoe (14106).py', 'r') as f2:
    framework_code = f1.read()
    debug_code = f2.read()

exec (framework_code + debug_code)

################################################################################


class TestSequenceFunctions(unittest.TestCase):

    tst = Zoe_14106_14106(0)

    def setUp(self):
        print("\n###setUp")
        with open("../src/credentials.txt") as f:
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
