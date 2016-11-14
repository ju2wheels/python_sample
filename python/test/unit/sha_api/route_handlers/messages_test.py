"""
The `test.unit.sha_api.route_handlers.messages_test` module provides unit tests for the messages endpoint handler
methods in `sha_api.route_handlers.messages`.

Classes:
    TestMessagesEndpoints: A unit test class for the messages endpoint handler methods.
"""

import hashlib
import sqlite3
import unittest

from mock import MagicMock, patch
from sha_api.route_handlers.messages import add_message, retrieve_message

import sha_api

class TestMessagesEndpoints(unittest.TestCase):
    """
    A unit test class for the messages endpoint handler methods.

    Methods:
        setUp: Unit test initialization.
        test_add_message: Tests that we can properly add a message or get the expected error response.
    """

    def setUp(self):
        """
        Initializes the unit test global configs
        """

        self.maxDiff = None # pylint: disable=invalid-name

    @patch(u'sha_api.route_handlers.messages.request')
    @patch(u'sha_api.route_handlers.messages.response')
    def test_add_message(self, message_response, message_request):
        """
        Tests that we can properly add a message or get the expected error response.
        """

        self.assertTrue(sha_api.route_handlers.messages.request is message_request)
        self.assertTrue(sha_api.route_handlers.messages.response is message_response)

        # Branch 1: Test that we get a 400 response with an invalid content type repsonse:

        message_request.json = None

        self.assertDictEqual(add_message(MagicMock(spec=sqlite3.Connection)),
                             {u'err_msg': u'Invalid content type, expected JSON'})
        self.assertEqual(message_response.status, 400)

        message_request.reset()
        message_response.reset()

        # Branch 2: Test that we get a 400 response with an invalid JSON request response

        message_request.json = {u'message': None}

        self.assertDictEqual(add_message(MagicMock(spec=sqlite3.Connection)),
                             {u'err_msg': u'Invalid JSON request, no message key found'})
        self.assertEqual(message_response.status, 400)

        message_request.reset()
        message_response.reset()

        # Branch 3: Test that we get a 500 response when we fail to insert record into db.

        message_request.json = {u'message': u'foobar'}
        db_mock = MagicMock(spec=sqlite3.Connection)
        db_mock.execute.side_effect = Exception(u'insert went foobar')

        self.assertDictEqual(add_message(db_mock),
                             {u'err_msg': u'Failed to add message and its SHA256 digest to database'})
        self.assertEqual(message_response.status, 500)

        message_request.reset()
        message_response.reset()

        # Branch 4: Test that we get the expected response back when there is no error

        message_request.json = {u'message': u'foobar'}

        self.assertDictEqual(add_message(MagicMock(spec=sqlite3.Connection)),
                             {u'digest': hashlib.sha256(u'foobar').hexdigest().upper()})

        message_request.reset()
        message_response.reset()

    @patch(u'sha_api.route_handlers.messages.request')
    @patch(u'sha_api.route_handlers.messages.response')
    def test_retrieve_message(self, message_response, message_request):
        """
        Tests that we can properly retrieve a message or get the expected error response.
        """

        self.assertTrue(sha_api.route_handlers.messages.request is message_request)
        self.assertTrue(sha_api.route_handlers.messages.response is message_response)

        digest = hashlib.sha256(u'foobar').hexdigest().upper()

        # Branch 1: Test that we get a 500 response and an error response of failing to retrieve message from db

        db_mock = MagicMock(spec=sqlite3.Connection)
        db_mock.execute.side_effect = Exception(u'select went foobar')

        self.assertDictEqual(retrieve_message(digest, db_mock),
                             {u'err_msg': u'Failed to retrieve message for the provided SHA256 digest from database'})
        self.assertEqual(message_response.status, 500)

        message_request.reset()
        message_response.reset()

        # Branch 2: Test that we get back the expected message when successfully retrieved.

        db_fetch = MagicMock()
        db_fetch.fetchone.return_value = (u'foobar',)
        db_mock = MagicMock(spec=sqlite3.Connection)
        db_mock.execute.return_value = db_fetch

        self.assertDictEqual(retrieve_message(digest, db_mock),
                             {u'message': u'foobar'})

        message_request.reset()
        message_response.reset()

        # Branch 3: Test that we get the a 404 response and a message not found error when message isnt found

        db_fetch = MagicMock()
        db_fetch.fetchone.return_value = None
        db_mock = MagicMock(spec=sqlite3.Connection)
        db_mock.execute.return_value = db_fetch

        self.assertDictEqual(retrieve_message(digest, db_mock),
                             {u'err_msg': u'Message not found'})
        self.assertEqual(message_response.status, 404)

        message_request.reset()
        message_response.reset()
