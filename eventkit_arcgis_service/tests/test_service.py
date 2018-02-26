# -*- coding: utf-8 -*-
from __future__ import absolute_import

import logging

from django.test import TestCase, override_settings
from mock import patch, Mock
from django.contrib.auth.models import User
from django.conf import settings
from ..auth import (get_user, Unauthorized, InvalidOauthResponse, request_access_token, get_user_data_from_schema,
                    fetch_user_from_token, OAuthServerUnreachable, OAuthError, Error)
import requests
import requests_mock
import json

logger = logging.getLogger(__name__)

@override_settings(OAUTH_AUTHORIZATION_URL="http://example.url/authorize")
class TestService(TestCase):

    def setUp(self):
        self.mock_requests = requests_mock.Mocker()
        self.mock_requests.start()
        self.addCleanup(self.mock_requests.stop)

    def test_get_user(self):