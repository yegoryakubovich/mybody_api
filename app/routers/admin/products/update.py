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

from app.services import ProductService
from app.utils import Response, Router

router = Router(
    prefix='/update'
)


class ProductUpdateByAdminSchema(BaseModel):
    token: str = Field(min_length=32, max_length=64)
    id: int = Field()
    type: str = Field(default=None, min_length=2, max_length=16)
    unit: str = Field(default=None, min_length=2, max_length=4)
    fats: int = Field(default=None)
    proteins: int = Field(default=None)
    carbohydrates: int = Field(default=None)
    calories: int = Field(default=None)
    article_id: int = Field(default=None)


@router.post()
async def route(schema: ProductUpdateByAdminSchema):
    result = await ProductService().update_by_admin(
        token=schema.token,
        id_=schema.id,
        type_=schema.type,
        unit=schema.unit,
        fats=schema.fats,
        proteins=schema.proteins,
        carbohydrates=schema.carbohydrates,
        calories=schema.calories,
        article_id=schema.article_id,
    )
    return Response(**result)
