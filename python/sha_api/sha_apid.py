"""
`sha_api.sha_apid` is the entrypoint of the sha_apid daemon for our REST API.

Constants:
    ROUTES: Defines the routes for our sha_apid daemon REST API and their handlers.

Methods:
    main: The entrypoint method for setuptools that instantiates our REST API, configures the routes, and starts the
          REST API.
"""

# pragma: no cover

import bottle

from sha_api.mybottle.sha_api_bottle import global_config, ShaApiBottle
from sha_api.route_handlers.messages import add_message, retrieve_message

ROUTES = [
    {
        u'callback': add_message,
        u'path': u'/messages',
        u'method': u'POST'
    },
    {
        u'callback': retrieve_message,
        u'path': u'/messages/<digest>',
        u'method': u'GET'
    }
]

def main(): # pragma: no cover
    """
    `setuptools` entrypoint for sha_apid or for running manually.
    """

    app = ShaApiBottle(ROUTES)

    bottle.run( # pylint: disable=no-member
        app,
        debug=global_config(app.config, u'sha_api', u'debug', True),
        host=global_config(app.config, u'sha_api', u'host', u'localhost'),
        port=global_config(app.config, u'sha_api', u'port', 8080),
        server=global_config(app.config, u'sha_api', u'server', u'wsgiref')
    )

if __name__ == u'__main__': # pragma: no cover
    main()
