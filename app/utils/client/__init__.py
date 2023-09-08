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


from json import JSONDecodeError

from fastapi import Request

from app.repositories import SessionRepository
from app.utils.client.device import Device


host = None
device = None
account = None


async def init(request: Request = None):
    global host, device, account
    host = request.client.host
    device = Device(headers=request.headers)
    account = None
    try:
        req = request
        json = await req.json()
        token = json.get('token')
        if token:
            account = await SessionRepository().get_account_by_token(token=token)
    except JSONDecodeError:
        pass
