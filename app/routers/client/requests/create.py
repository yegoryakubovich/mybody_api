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


from pydantic import BaseModel, Field
from fastapi.responses import Response as FastapiResponse

from app.services import RequestService
from app.utils import Router, Response


router = Router(
    prefix='/create',
)


class RequestCreateSchema(BaseModel):
    phone: str = Field(min_length=1, max_length=16)
    name: str = Field(min_length=1, max_length=64)


@router.post()
async def route(schema: RequestCreateSchema):
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST, OPTIONS',
        'Access-Control-Allow-Headers': 'DNT,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range',
        'Access-Control-Expose-Headers': 'Content-Length,Content-Range',
    }
    result = await RequestService().create(phone=schema.phone, name=schema.name)
    return Response(**result, headers=headers)


@router.options('')
async def route(response: FastapiResponse):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'DNT,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range'
    response.headers['Access-Control-Expose-Headers'] = 'Content-Length,Content-Range'
    return {}
