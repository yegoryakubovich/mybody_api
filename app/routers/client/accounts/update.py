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

from app.services import AccountService
from app.utils import Response, Router


router = Router(
    prefix='/update'
)


class AccountUpdateSchema(BaseModel):
    token: str = Field(min_length=32, max_length=64)
    username: str = Field(min_length=6, max_length=32, default=None)
    firstname: str = Field(max_length=32, default=None)
    lastname: str = Field(max_length=32, default=None)
    surname: str = Field(max_length=32, default=None)
    country: str = Field(max_length=16, default=None)
    language: str = Field(max_length=32, default=None)
    timezone: str = Field(max_length=16, default=None)
    currency: str = Field(max_length=16, default=None)


@router.post()
async def route(schema: AccountUpdateSchema):
    result = await AccountService().update(
        token=schema.token,
        username=schema.username,
        firstname=schema.firstname,
        lastname=schema.lastname,
        surname=schema.surname,
        country_id_str=schema.country,
        language_id_str=schema.language,
        timezone_id_str=schema.timezone,
        currency_id_str=schema.currency,
    )
    return Response(**result)
