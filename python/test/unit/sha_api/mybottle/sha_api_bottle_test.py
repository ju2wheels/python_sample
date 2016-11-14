"""
The `test.unit.sha_api.mybottle.sha_api_bottle_test` module provides unit tests for the `ShaApiBottle` class in
`sha_api.mybottle.sha_api_bottle`.

Classes:
    TestShaApiBottle: A unit test class for the `ShaApiBottle` class.
"""

import json
import tempfile
import unittest

from bottle import ConfigDict # pylint: disable=no-name-in-module
from mock import MagicMock, patch
from sha_api.mybottle.sha_api_bottle import global_config, ShaApiBottle
from sha_api.sha_apid import ROUTES

import sha_api

class TestShaApiBottle(unittest.TestCase):
    """
    A unit test class for the `ShaApiBottle` class.

    Methods:
        setUp: Unit test initialization.
        test_error_handler: Tests to ensure the error handler returns a JSON value.
        test_global_config: Tests to ensure we get the correct values from a `ConfigDict` instance.
        test_sha_api_constructor: Tests that `ShaApiBottle` instance can be properly instantiated without throwing any
                                  exceptions.
    """

    def setUp(self):
        """
        Initializes the unit test global configs
        """

        self.maxDiff = None # pylint: disable=invalid-name
        self.config_sample = tempfile.NamedTemporaryFile(delete=False)
        self.dbfile = tempfile.NamedTemporaryFile(delete=False)
        self.os_environ = {u'SHA_API_CONFIG': self.config_sample.name}

        self.configdict_ns = ConfigDict().load_dict(
            {
                u'sha_api': {
                    u'test_variable': u'test_value'
                },
                u'sqlite': {
                    u'dbfile': self.dbfile.name
                }
            }
        )

        with open(self.config_sample.name, 'w') as fout:
            fout.write(u"[sha_api]\ntest_variable = test_value\n[sqlite]\ndbfile = %s" % self.dbfile.name)

    def test_error_handler(self):
        """
        Tests to ensure the error handler returns a JSON value.
        """

        res = MagicMock()
        res_json = json.dumps({u'err_msg': u'Response Body'})

        res.body = u'Response Body'

        api = ShaApiBottle(ROUTES)

        self.assertEqual(api.default_error_handler(res), res_json)

    def test_global_config(self):
        """
        Tests to ensure we get the correct values from a `ConfigDict` instance.
        """

        self.assertEqual(global_config(self.configdict_ns, u'sqlite', u'dbfile', u'Not Found'), self.dbfile.name)

    def test_sha_api_constructor(self):
        """
        Tests that `ShaApiBottle` instance can be properly instantiated without throwing any exceptions.
        """

        # Branch 1: Nothing throws an error and all goes well
        try:
            api = ShaApiBottle(ROUTES) # pylint: disable=unused-variable
        except Exception as err: # pylint: disable=broad-except
            self.fail(u'ShaApiBottle sha_api instance failed to initialize: %s' % str(err))

        # Branch 2: When routes object is not a list we get a proper assert error

        with self.assertRaises(AssertionError) as err:
            api = ShaApiBottle(dict())

        self.assertEqual(str(err.exception), u'routes must be an array of route dicts to be passed to bottle.route')

        # Branch 3: When routes object is a list but it doesnt contain dict items we get a proper assert error

        with self.assertRaises(AssertionError) as err:
            api = ShaApiBottle([False])

        self.assertEqual(str(err.exception), u'route must be a dict that can be passed to bottle.route')

        # Branch 4: When environment variable specifies config file it is properly loaded.

        with patch.dict(u'sha_api.mybottle.sha_api_bottle.os.environ', values=self.os_environ):
            self.assertEqual(self.os_environ[u'SHA_API_CONFIG'],
                             sha_api.mybottle.sha_api_bottle.os.environ.get(u'SHA_API_CONFIG'))

            api = ShaApiBottle(ROUTES)

            self.assertEqual(api.config.get(u'sha_api.test_variable'), u'test_value')
            self.assertEqual(api.config.get(u'sqlite.dbfile'), self.dbfile.name)

        # Branch 5: When any portion of the db initialization fails it should just bubble up the exception

        with patch(u'sha_api.mybottle.sha_api_bottle.sqlite3.connect') as sqlite_connect:
            self.assertEqual(sqlite_connect, sha_api.mybottle.sha_api_bottle.sqlite3.connect)

            sqlite_connect.side_effect = Exception(u'sqlite exception')

            with self.assertRaises(Exception) as err:
                api = ShaApiBottle()

            self.assertEqual(str(err.exception), u'sqlite exception')
