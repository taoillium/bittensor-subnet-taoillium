import sys
import unittest
import os
import services.security as security
import services.config as config

class SecurityTestCase(unittest.TestCase):
    """
    This class contains unit tests for the security module.
    """

    def setUp(self):
        self.uid = os.getenv("TEST_UID","1")

    def test_create_manage_access_token(self):
        token = security.create_manage_access_token({"id": self.uid, "chain": "bittensor", "roles": ["wallet-manage"]})
        print(token)
        self.assertIsNotNone(token)

    def test_verify_manage_token(self):
        token = security.create_manage_access_token({"id": self.uid, "chain": "bittensor", "roles": ["wallet-manage"]})
        self.assertIsNotNone(token)
        self.assertTrue(security.verify_manage_token(token))


