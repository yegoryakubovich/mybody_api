#
# (c) 2023, Yegor Yakubovich, yegoryakubovich.com, personal@yegoryakybovich.com
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#


import logging

from fastapi import FastAPI
from starlette.middleware.base import BaseHTTPMiddleware

from app.db import create_models
from app.utils.middleware import Middleware
from app.routers import routers


app = FastAPI(
    title='My Body API',
    version='0.1',
    contact={
        'name': 'Yegor Yakubovich',
        'url': 'https://yegoryakubovich.com',
        'email': 'personal@yegoryakubovich.com',
    },
    license_info={
        'name': 'Apache 2.0',
        'url': 'https://www.apache.org/licenses/LICENSE-2.0.html',
    },
)


app.add_middleware(middleware_class=BaseHTTPMiddleware, dispatch=Middleware())
for router in routers:
    app.include_router(router)


def create_app():
    logging.basicConfig(level=logging.DEBUG)
    logging.info(msg='Application starting...')

    create_models()
    return app
