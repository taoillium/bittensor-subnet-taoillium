import sys
import unittest

import services.security as security

class SecurityTestCase(unittest.TestCase):
    """
    This class contains unit tests for the security module.
    """

    def setUp(self):
        pass

    def test_create_manage_access_token(self):
        token = security.create_manage_access_token({"id": 1, "providerId": "bittensor", "roles": ["wallet-manage"], "_admin": "admin"})
        print(token)
        self.assertIsNotNone(token)

    def test_verify_manage_token(self):
        token = security.create_manage_access_token({"id": 1, "providerId": "bittensor", "roles": ["wallet-manage"], "_admin": "admin"})
        self.assertIsNotNone(token)
        self.assertTrue(security.verify_manage_token(token))


