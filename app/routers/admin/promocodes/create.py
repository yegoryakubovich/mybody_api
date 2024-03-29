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


from datetime import date

from pydantic import BaseModel, Field

from app.services import PromocodeService
from app.utils import Router, Response


router = Router(
    prefix='/create',
)


class PromocodeCreateByAdminSchema(BaseModel):
    token: str = Field(min_length=32, max_length=64)
    id_str: str = Field(min_length=1, max_length=16)
    usage_quantity: int = Field()
    date_from: date = Field()
    date_to: date = Field()
    type: str = Field(min_length=1, max_length=16)


@router.post()
async def route(schema: PromocodeCreateByAdminSchema):
    result = await PromocodeService().create_by_admin(
        token=schema.token,
        id_str=schema.id_str,
        usage_quantity=schema.usage_quantity,
        date_from=schema.date_from,
        date_to=schema.date_to,
        type_=schema.type,
    )
    return Response(**result)
