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


from fastapi import Depends
from pydantic import BaseModel, Field

from app.services import TrainingService
from app.utils import Response, Router


router = Router(
    prefix='/list/get'
)


class TrainingGetListSchema(BaseModel):
    token: str = Field(min_length=32, max_length=64)
    account_service_id: int = Field()


@router.get()
async def route(schema: TrainingGetListSchema = Depends()):
    result = await TrainingService().get_list(
        token=schema.token,
        account_service_id=schema.account_service_id,
    )
    return Response(**result)
