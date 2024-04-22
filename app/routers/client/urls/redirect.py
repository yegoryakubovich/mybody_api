#
# (c) 2024, Yegor Yakubovich, yegoryakubovich.com, personal@yegoryakybovich.com
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


from fastapi.responses import RedirectResponse
from app.services import UrlService
from app.utils import Router
from fastapi import Request

router = Router(
    prefix='/{redirect}'
)


@router.get()
async def route(request: Request, redirect: str):
    client_ip = request.client.host
    url = await UrlService().get_by_name(
        name=redirect,
    )
    await UrlService().record_click(
        url_name=url['url']['name'],
        client_ip=client_ip,
    )
    return RedirectResponse(url=url['url']['redirect'])
