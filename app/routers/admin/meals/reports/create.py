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

from fastapi import UploadFile, Depends
from pydantic import Field, BaseModel

from app.services import MealReportService
from app.utils import Response, Router


router = Router(
    prefix='/create',
)


class MealReportCreateByAdminSchema(BaseModel):
    token: str = Field(min_length=32, max_length=64)
    meal_id: int = Field()
    comment: Optional[str] = Field(default=None)
    products: Optional[str] = Field(default=None)


@router.post()
async def route(
        schema: MealReportCreateByAdminSchema = Depends(),
        images: Optional[list[UploadFile]] = None,
):
    result = await MealReportService().create_by_admin(
        token=schema.token,
        meal_id=schema.meal_id,
        comment=schema.comment,
        images=images,
        products=schema.products,
    )
    return Response(**result)
