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


from pydantic import BaseModel, Field

from app.services import AccountServiceService
from app.utils import Response, Router


router = Router(
    prefix='/create',
)


class AccountServiceCreateSchema(BaseModel):
    token: str = Field(min_length=32, max_length=64)
    account_username: str = Field(min_length=6, max_length=32)
    service_id_str: str = Field(min_length=2, max_length=128)
    answers: str = Field(min_length=2, max_length=8192)
    state: str = Field(min_length=2, max_length=128)


@router.post()
async def route(schema: AccountServiceCreateSchema):
    result = await AccountServiceService().create(
        token=schema.token,
        account_username=schema.account_username,
        service_id_str=schema.service_id_str,
        answers=schema.answers,
        state=schema.state,
    )
    return Response(**result)
