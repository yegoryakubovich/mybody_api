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
    prefix='/update',
)


class AccountServiceUpdateSchema(BaseModel):
    token: str = Field(min_length=32, max_length=64)
    id_: int = Field()
    answers: str = Field(default=None, min_length=2, max_length=8192)
    state: str = Field(default=None, min_length=2, max_length=128)


@router.post()
async def route(schema: AccountServiceUpdateSchema):
    result = await AccountServiceService().update(
        token=schema.token,
        id_=schema.id_,
        answers=schema.answers,
        state=schema.state,
    )
    return Response(**result)
