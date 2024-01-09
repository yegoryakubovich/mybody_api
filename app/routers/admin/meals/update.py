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


from datetime import date as datetime_date

from pydantic import BaseModel, Field

from app.services import MealService
from app.utils import Response, Router


router = Router(
    prefix='/update'
)


class MealUpdateByAdminSchema(BaseModel):
    token: str = Field(min_length=32, max_length=64)
    id: int = Field()
    date: datetime_date = Field(default=None)
    type: str = Field(default=None, max_length=16)


@router.post()
async def route(schema: MealUpdateByAdminSchema):
    result = await MealService().update_by_admin(
        token=schema.token,
        id_=schema.id,
        date_=schema.date,
        type_=schema.type,
    )
    return Response(**result)
