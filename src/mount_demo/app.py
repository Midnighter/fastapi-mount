# Copyright (c) 2019, Moritz E. Beber.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


"""Provide the main application."""


import asyncio
import logging
import warnings

from fastapi import FastAPI
from starlette.responses import UJSONResponse

from mount_demo import settings


app = FastAPI(
    title="FastAPI Mount Demo",
    description="A prototype of mounting the main FastAPI app under "
                "SCRIPT_NAME.",
    openapi_prefix=settings.SCRIPT_NAME,
)


@app.on_event('startup')
async def init():
    msg_format = "[%(name)s] [%(levelname)s] %(message)s"
    if settings.DEBUG:
        asyncio.get_event_loop().set_debug(True)
        warnings.simplefilter("always", ResourceWarning)
        logging.basicConfig(level="DEBUG", format=msg_format)
        app.debug = True
    else:
        logging.basicConfig(level="INFO", format=msg_format)


@app.get("/hello")
async def say_hello():
    return UJSONResponse({"message": "hello world"})


@app.get("/bye")
async def say_bye():
    return UJSONResponse({"message": "goodbye"})
