# FastAPI Mount Demonstration

[![License](https://img.shields.io/badge/license-Apache--2.0-blueviolet)](https://opensource.org/licenses/Apache-2.0)

A minimal application for prototyping mounting the main FastAPI at a sub path.

## Rationale

Typically, an application expects to be seated at the root of a domain , for
example, this application defines two endpoints `/hello` and `/bye` which you
can hit locally (after a `make start` command) at `localhost:8000/hello` and
`localhost:8000/bye`. However, sometimes we might want to 'mount' an application
at a sub path. This may be the case in a microservice setting where many
services are sitting behind a reverse proxy and should be addressed at the same
domain (see the figure below from https://traefik.io). The FastAPI documentation
[explains]( https://fastapi.tiangolo.com/tutorial/sub-applications-proxy/) some
of the problems that occur in such a situation.

![traefik proxy schema](https://docs.traefik.io/img/internal.png)

As an example, let's assume you have two services `user-service` and
`shopping-cart`. Both applications were created in a way that they expect to be
at the root, however, now we want to address them at different paths on the same
domain. This could be `api.domain.com/user-service` and
`api.domain.com/shopping-cart`. The application itself should not really be
involved in this. Where it is being deployed is outside of its scope and we
certainly don't want to edit all our route definitions.

It turns out that the `SCRIPT_NAME` HTTP header was created for exactly this
purpose. Instead of letting the proxy manipulate this header with every request,
it is fairly standard to let it be configurable by an environment variable. A
popular option is
[gunicorn](https://docs.gunicorn.org/en/stable/faq.html#wsgi-bits) in
combination with
[Flask](https://flask.palletsprojects.com/en/1.1.x/config/?highlight=script_name#APPLICATION_ROOT).
In Flask this is internally handled by werkzeug [as shown
here](https://werkzeug.palletsprojects.com/en/0.15.x/wsgi/?highlight=script_name#werkzeug.wsgi.pop_path_info).

_How do we do this with FastAPI (or Starlette)?_

## Solution

The first key to the puzzle is to realize that with Starlette and FastAPI we are
dealing with an [ASGI](https://asgi.readthedocs.io/) and _not_ a
[WSGI](https://wsgi.readthedocs.io/) application. The two specifications are
similar with regard to their special keys but not identical.  [As it turns
out](https://asgi.readthedocs.io/en/latest/specs/www.html#wsgi-compatibility)
the corresponding key for `SCRIPT_NAME` is `root_path`.

Following this realization, we will want to configure the `root_path`. This
depends a lot on your deployment strategy. For this demo we have chosen
[gunicorn](https://gunicorn.org/) with [uvicorn](https://www.uvicorn.org/)
workers.  Uvicorn has [a lot of useful command line
options](https://www.uvicorn.org/settings/) and we want to [use `--root-path` as
well as `--proxy-headers`](https://www.uvicorn.org/settings/#http) here.

Since we are only using uvicorn workers within gunicorn, we cannot use command
line options but rather need to configure the workers directly. This is done via
a subclass [as explained in this
issue](https://github.com/encode/uvicorn/issues/266). You can look at the way we
have chosen to do so for this project in the
[workers.py](src/mount_demo/workers.py) module (code excerpt below).

```python
from starlette.config import Config
from uvicorn.workers import UvicornWorker


config = Config()


class ConfigurableWorker(UvicornWorker):
    """
    Define a UvicornWorker that can be configured by modifying its class attribute.

    All of the command line options for uvicorn are potential configuration options
    (see https://www.uvicorn.org/settings/ for the complete list).

    """

    #: dict: Set the equivalent of uvicorn command line options as keys.
    CONFIG_KWARGS = {
        "root_path": config("SCRIPT_NAME", default=""),
        "proxy_headers": True,
    }
```

We have chosen here to still rely on the environment variable `SCRIPT_NAME` to
finally configure the `root_path`. By default this string is empty and the
application will listen at the root. Here, we have set this to be
`/demo-service`. Together with the [proxy configuration](nginx.conf), you can
now let the application say hello at
`http://localhost/demo-service/hello`. The benefit here being that we can now
mount the app on any path of our choosing simply by changing the environment
variable `SCRIPT_NAME` and the corret URL rewrite in the proxy configuration. It
also means that we can now expose as many services as we like behind the same
domain name simply by choosing different paths for them.

But not so fast you say! What about the [OpenAPI](https://www.openapis.org/)
docs? Well, as it turns out (at least for the moment) we still have to insert a
prefix for those to work properly (see code below from
[app.py](src/mount_demo/app.py)). It would make sense for the `root_path` to be
used automatically, though, so keep your eyes peeled for [the corresponding
issue](https://github.com/tiangolo/fastapi/issues/461) on FastAPI.

```python
app = FastAPI(
    title="FastAPI Mount Demo",
    description="A prototype of mounting the main FastAPI app under "
                "SCRIPT_NAME.",
    openapi_prefix=settings.SCRIPT_NAME,
)
```

## Acknowledgements

Thanks to the user @euri10 for the helpful discussions and advice on
[gitter](https://gitter.im/tiangolo/fastapi).

## Copyright

* Copyright © 2019, Moritz E. Beber. All rights reserved.
* Free software licensed under the [Apache Software License 2.0](LICENSE).
* This README and other documentation are licensed under a [Creative Commons
  Attribution-ShareAlike 4.0 International
  License](http://creativecommons.org/licenses/by-sa/4.0/).

  [![Creative Commons Attribution-ShareAlike 4.0 International
  License](https://i.creativecommons.org/l/by-sa/4.0/88x31.png)](http://creativecommons.org/licenses/by-sa/4.0/)
