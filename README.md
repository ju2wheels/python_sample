# sha_api
---

This project was created as an interview sample project. It highlights combining `Docker` with `Python` unit testing using `nose` and `mock` and packaging with `setuptools`.

Python specific packaging details can be found here:

|Resource                                                                                                        |Description                                                                  |
|----------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------|
|[setuptools](http://setuptools.readthedocs.io/en/latest/setuptools.html#configuring-setup-using-setup-cfg-files)|Python `setuptools` documentation.                                           |
|[pkg_resources](http://setuptools.readthedocs.io/en/latest/pkg_resources.html)                                  |Python `pkg_resources` documentation for finding and using package resources.|
|[setup.py setuptools template](https://gist.github.com/ju2wheels/0c52e997b513a4b4c5bd)                          |Python `setuptools` template with comments.                                  |
|[nose](http://nose.readthedocs.io/en/latest/testing.html)                                                       |Python `nose` unit testing documentation.                                    |

If you are test running the included code, please note that you may have to regenerate the self signed HTTPS cert included in the Docker image in order to get the HTTPS to work.

---

`sha_api` is a REST API using `bottle` that stores messages based on their `SHA256` digest and allows easy retrieval.

## Supported Python versions and Platforms

**Python Versions**: 2.7 (3.2+ should work ok as well but not tested)

**Platforms**: Linux

## Requirements

* Python
  * bottle
  * bottle-sqlite
  * coverage
  * mock
  * nose
  * nose-cov
  * pip
  * setuptools
* RPMs
  * nginx
  * supervisor
* Other
  * docker
  * docker-compose
  * make

Please ensure you have `docker`, `docker-compose`, and `make` installed on your `dev` machine before beginning below. It is assumed that the current user can run the `docker` and `docker-compose` command without needing to use `sudo` to acquire root.

## Building `sha_api`

A `sha_api` `docker` image can be built using the `make build` target. 

```
$ make build
```

## Running `sha_api`

A `sha_api` `docker` instance can be run using the `make run` target:

```
$ make run
```

## Testing `sha_api`

In order to run tests against `sha_api` you need to ensure your current active environment Python (system or virtual environment) is version 2.7 and the above Python requirements are installed (`pylint` can be optionally installed as well for linting).

Once all the dependencies are installed you can run the `nose` unit tests by running the `make test` target.

```
$ make test
```

## Configuration

The `sha_api` container has a `/data` volume which has the following structure:

|Volume Path                   |Description|
|------------------------------|-----------|
|/data/etc/sha_api/sha_api.conf|The `bottle` configuration file for the `sha_apid` REST API daemon. THe ini style format is described in the [bottle Configuration](http://bottlepy.org/docs/dev/configuration.html) guide.|
|/data/etc/nginx/*             |All `nginx` configuration files from this directory are copied into `/etc/nginx` when the container starts (it does not do a recursive copy. The default image includes `/etc/nginx/nginx.conf`, `/etc/nginx/server.crt`, and `/etc/nginx/server.key`.|
|/data/sha_api.db              |This is the `sqlite` database used by the `sha_apid` service to store messages. This is automatically created and initialized if not present.|
|/data/var/log                 |The application logs are contained here. The `sha_apid` REST API logs are automatically rotated by `supervisord` but the `nginx` logs are not currently rotated.|

By overriding the `sha_api.conf` and the `nginx` configuration files, the entire REST API and SSL reverse proxy can be reconfigured.

Example `sha_api.conf`:

```
[bottle]
debug = True

[sha_api]
debug = True
host = 0.0.0.0
port = 8080
server = wsgiref

[sqlite]
dbfile = /data/sha_api.db
```

## `sha_api` REST API Endpoints

|Endpoint          |HTTP Request Type|Description|
|------------------|-----------------|-----------|
|/messages         |POST             |A message of the structure `{"message": "message data"}` can be submitted for storage.|
|/messages/<digest>|GET              |The message with the requested `SHA256` digest is retrieved.|

Example requests using `curl` (**Note: We are using `-k` to disable verification of the built in SSL cert as it self signed**):

```
$ make run

# In a separate terminal:

$ curl -k -v -X POST -H "Content-Type: application/json" -d '{"message": "foo"}' https://localhost/messages
$ curl -k -v https://localhost/messages/2c26b46b68ffc68ff99b453c1d30413413422d706483bfa0f98a5e886266e7ae
$ curl -k -v https://localhost/messages/badshasum
```

## Questions

1. How would your implementation scale if this were a high throughput service?
    > My current implementation has a few short comings. The `sha_apid` REST API service is using the default `wsgiref` web server which does not support true threading and will therefor limit response handling. This example also uses `sqlite` as the backend instead of a more production oriented db like `PostgreSQL`, and as such the db wrapper is very plain and opens/closes the db connection after each endpoint request. I bundled `nginx` with the backend REST API for demonstration purposes but in general these should be separate. 
2. How could you improve that?
    > To resolve the resquest processing throughput, the `wsgiref` web server would need to be replaced by a proper threading web front end for the REST API. The database shim that `bottle` uses would need to be replaced by one for a more production ready database, and preferrably it would support connection pooling so that the `sha_apid` can maintain a pool of connections and allow each threaded request to quickly get a db handle as necessary. For the `nginx` SSL reverse proxy, this should be removed from the backend REST API container and be placed as close to the requester as possible versus closer to the REST API as it is now. By moving `nginx` to the beginning or the request change it can be placed in front of a round robin `sha_api` instances to process requests.
