"""
`sha_api.route_handlers.messages` provides route handler methods for the /messages/* REST API endpoints.

Methods:
    add_message: REST endpoint for POST to /messages. Adds the provided message to the database.
    retrieve_message: REST endpoint for GET to /messages/<digest>. Retrieves the message with the requested digest from
                      the database.
"""

import hashlib

from bottle import request, response # pylint: disable=no-name-in-module

def add_message(db): # pylint: disable=invalid-name
    """
    Adds a message and its SHA256 digest to the database.

    Args:
        db: A Sqlite3 db connection handle.
    """

    if request.json is None:
        response.status = 400
        return {u'err_msg': u'Invalid content type, expected JSON'}

    if request.json.get(u'message') is None:
        response.status = 400
        return {u'err_msg': u'Invalid JSON request, no message key found'}

    message = request.json.get(u'message').decode(u'utf-8')
    sha256_digest = hashlib.sha256(message).hexdigest().upper()

    try:
        with db:
            db.execute(u'INSERT OR REPLACE INTO sha_api (digest, message) VALUES (?, ?)', (sha256_digest, message))
    except Exception: # pylint: disable=broad-except
        response.status = 500
        return {u'err_msg': u'Failed to add message and its SHA256 digest to database'}

    return {u'digest': sha256_digest}

def retrieve_message(digest, db): # pylint: disable=invalid-name
    """
    Returns the message associated with the SHA256 digest from the database or an error message if not found.

    Args:
        db: A Sqlite3 db connection handle.
        digest: The SHA256 digest of the message to retrieve.
    """

    try:
        row = db.execute(u'SELECT message FROM sha_api WHERE digest = ?', (digest.decode(u'utf-8').upper(),)).fetchone()

        if row is not None:
            message = row[0]
        else:
            message = None
    except Exception: # pylint: disable=broad-except
        response.status = 500
        return {u'err_msg': u'Failed to retrieve message for the provided SHA256 digest from database'}

    if message is not None:
        return {u'message': message}
    else:
        response.status = 404
        return {u'err_msg': u'Message not found'}
