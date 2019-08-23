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

1. If you start this service without further actions you can visit the exposed
    routes and documentation at:

    * `localhost:8000/hello`
    * `localhost:8000/bye`
    * `localhost:8000/docs`
    * `localhost:8000/redoc`

2. In order to switch it up, we can now use a reverse proxy. One has already
   been defined for you in the [docker-compose
   configuration](docker-compose.yml). When you now try to access your service
   through the proxy at `http://localhost/demo-service/hello` you will see that
   this fails with a 404.

3. We can rescue the situation by rewriting the URL in the proxy instead. You
   can try this by instead hitting `http://localhost/demo2-service/hello`. This
   will give you the correct response but if you now visit
   `http://localhost/demo2-service/docs` that fails because the app itself is
   unaware of the rewritten path.

4. To try and remedy the situation, you can create a `.env` file with the
   content:

    ```
    SCRIPT_NAME=/demo2-service
    ```

    This will automatically be used by the docker-compose configuration so just
    restart the service (`make clean && make start`). Setting `SCRIPT_NAME` to a
    non-empty string will affect how the application is initialized.

    ```python
    app = FastAPI(
        title="FastAPI Mount Demo",
        description="A prototype of mounting the main FastAPI app under "
                    "SCRIPT_NAME.",
        openapi_prefix=settings.SCRIPT_NAME,
    )
    ```

    When you now visit the docs at `http://localhost/demo2-service/docs` it
    works as expected!

This is a working strategy but it is rather tedious. We had to rewrite the URL
in the reverse proxy and modify our application's source code (we still made it
configurable) to manually set the `openapi_prefix`. There should be a better
way.

## Copyright

* Copyright © 2019, Moritz E. Beber. All rights reserved.
* Free software licensed under the [Apache Software License 2.0](LICENSE).
