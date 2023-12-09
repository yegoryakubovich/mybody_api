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


from fastapi import Depends
from pydantic import BaseModel, Field

from app.services import AccountService
from app.utils import Router, Response


router = Router(
    prefix='/username/check',
)


class CheckAccountUsernameSchema(BaseModel):
    username: str = Field(min_length=6, max_length=32)


@router.get()
async def route(schema: CheckAccountUsernameSchema = Depends()):
    result = await AccountService().check_username(username=schema.username)
    return Response(**result)
