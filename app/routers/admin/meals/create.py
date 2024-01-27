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
    prefix='/create'
)


class MealCreateByAdminSchema(BaseModel):
    token: str = Field(min_length=32, max_length=64)
    account_service_id: int = Field()
    date: datetime_date = Field()
    type: str = Field(max_length=16)
    fats: int = Field()
    proteins: int = Field()
    carbohydrates: int = Field()


@router.post()
async def route(schema: MealCreateByAdminSchema):
    result = await MealService().create_by_admin(
        token=schema.token,
        account_service_id=schema.account_service_id,
        date_=schema.date,
        type_=schema.type,
        fats=schema.fats,
        proteins=schema.proteins,
        carbohydrates=schema.carbohydrates,
    )
    return Response(**result)
