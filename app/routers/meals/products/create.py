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

from app.services import MealProductService
from app.utils import Response, Router


router = Router(
    prefix='/create',
)


class MealProductCreateSchema(BaseModel):
    token: str = Field(min_length=32, max_length=64)
    meal_id: int = Field()
    product_id: int = Field()
    value: int = Field()


@router.post()
async def route(schema: MealProductCreateSchema):
    result = await MealProductService().create(
        token=schema.token,
        meal_id=schema.meal_id,
        product_id=schema.product_id,
        value=schema.value,
    )
    return Response(**result)
