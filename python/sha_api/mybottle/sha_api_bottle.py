"""
`sha_api.mybottle.sha_api_bottle` provides a new `bottle.Bottle` class and helper methods to drive the `sha_api`
REST API.

Classes:
    ShaApiBottle: A new `bottle.Bottle` type customized specifically for our `sha_api` REST API.

Methods:
    global_config: A wrapper around `bottle.ConfigDict` to retrieve a configuration setting either from the global app
                   config or its default value in both old format and the new namespace format.
"""

import json
import os
import sqlite3
import tempfile

import bottle

from bottle import response # pylint: disable=no-name-in-module
from bottle.ext import sqlite # pylint: disable=import-error,no-name-in-module

def global_config(config, config_namespace, config_namespace_prop, default):
    """
    Returns the configuration setting from the application `ConfigDict` instance or the default.
    """

    # This is the old ConfigDict format
    if config_namespace in config: # pragma: no cover
        # support for configuration before `ConfigDict` namespaces
        return config.get(config_namespace, {}).get(config_namespace_prop, default)
    else:
        return config.get(config_namespace + u'.' + config_namespace_prop, default)

class ShaApiBottle(bottle.Bottle): # pylint: disable=no-member,too-few-public-methods
    """
    `ShaApiBottle` provides a new `bottle.Bottle` class that by default always returns JSON responses on error
    and automatically installs sqlite support after loading configuration from an expected location if provided.

    Methods:
        default_error_handler: Overrides the error handler to always return JSON errors instead of HTML.
    """

    def __init__(self, routes=None):
        super(ShaApiBottle, self).__init__()

        if routes is not None:
            assert issubclass(routes.__class__, list), \
                u'routes must be an array of route dicts to be passed to bottle.route'

            for route in routes:
                assert issubclass(route.__class__, dict), u'route must be a dict that can be passed to bottle.route'

        if os.environ.get(u'SHA_API_CONFIG') is not None and \
           os.path.isfile(os.path.normpath(os.environ.get(u'SHA_API_CONFIG'))):
            config_file = os.path.normpath(os.environ.get(u'SHA_API_CONFIG'))
        # If coverage for the above works then this one is the same case so skip it
        elif os.path.isfile(u'/etc/sha_api/sha_api.conf'): # pragma: no cover
            config_file = u'/etc/sha_api/sha_api.conf'
        else:
            config_file = None

        if config_file is not None:
            self.config.load_config(config_file)

        sqlite_db_file = global_config(self.config, u'sqlite', u'dbfile', None)

        if sqlite_db_file is None:
            # Dont use the ':memory:' because they end up closing it after each route uses it, making it useless
            # for anything other than a temporary db cache since we wont be able to persist our primary table.
            temp_file = tempfile.NamedTemporaryFile(delete=False)
            sqlite_db_file = temp_file.name

        self.install(
            sqlite.Plugin(
                dbfile=sqlite_db_file
            )
        )

        # bind all the routes
        if routes is not None:
            for route in routes:
                self.route(**route)

        # Initialize the sqlite db
        db_con = sqlite3.connect(sqlite_db_file)

        db_con.execute("""
        CREATE TABLE IF NOT EXISTS sha_api (
            digest  TEXT,
            message TEXT,
            PRIMARY KEY (digest, message)
        );
        """)

        db_con.close()

    def default_error_handler(self, res): # pylint: disable=no-self-use
        """
        Override the default error handler to always return JSON instead of HTML (dont know why it does this, it makes
        no sense that they set the default content type to JSON then return HTML).
        """

        response.content_type = u'application/json'
        return json.dumps({u'err_msg': res.body})
