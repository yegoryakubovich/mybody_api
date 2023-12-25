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


from typing import Optional

from pydantic import BaseModel, Field

from app.services import AccountServiceService
from app.utils import Response, Router


router = Router(
    prefix='/additional/create',
)


class AccountServiceAdditionalCreateSchema(BaseModel):
    token: str = Field(min_length=32, max_length=64)
    service: str = Field(min_length=2, max_length=64)
    answers: Optional[str] = Field(min_length=2, max_length=8192, default=None)


@router.post()
async def route(schema: AccountServiceAdditionalCreateSchema):
    result = await AccountServiceService().create_additional(
        token=schema.token,
        service_id_str=schema.service,
        answers=schema.answers,
    )
    return Response(**result)
