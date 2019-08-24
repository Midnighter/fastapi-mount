# Copyright (c) 2018, Novo Nordisk Foundation Center for Biosustainability,
# Technical University of Denmark.
# Copyright (c) 2019, Moritz E. Beber.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


"""Configure the gunicorn server."""


import os


environment = os.environ["ENVIRONMENT"]

bind = "0.0.0.0:8000"
worker_class = "mount_demo.workers.ConfigurableWorker"
timeout = 20
accesslog = "-"
access_log_format = (
    '{'
    '"date": "%(t)s",'
    '"status_line": "%(r)s",'
    '"remote_address": "%(h)s",'
    '"status": "%(s)s",'
    '"response_length": "%(b)s",'
    '"request_time": "%(L)s",'
    '"referer": "%(f)s",'
    '}'
)
if environment == "production":
    workers = 2
    preload_app = True
    loglevel = "INFO"
else:
    workers = 2
    reload = True
    loglevel = "DEBUG"
