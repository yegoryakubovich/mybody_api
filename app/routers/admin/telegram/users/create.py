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
from typing import Optional

from pydantic import BaseModel, Field

from app.services import TelegramUserService
from app.utils import Router, Response


router = Router(
    prefix='/create',
)


class TelegramUserCreateByAdminSchema(BaseModel):
    token: str = Field(min_length=32, max_length=64)
    tg_id: int = Field()
    firstname: str = Field()
    start_url: str = Field()
    username: Optional[str] = Field(default=None)
    lastname: Optional[str] = Field(default=None)


@router.post()
async def route(schema: TelegramUserCreateByAdminSchema):
    result = await TelegramUserService().create_by_admin(
        token=schema.token,
        tg_id=schema.tg_id,
        firstname=schema.firstname,
        url_id_str=schema.start_url,
        username=schema.username,
        lastname=schema.lastname,
    )
    return Response(**result)
