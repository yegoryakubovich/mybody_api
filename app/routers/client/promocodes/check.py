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
from pydantic import Field, BaseModel
from app.services import PromocodeService
from app.utils import Router, Response


router = Router(
    prefix='/check',
)


class PromocodeCheckSchema(BaseModel):
    token: str = Field(min_length=32, max_length=64)
    id_str: str = Field(min_length=1, max_length=16)
    currency_cost_id: int = Field()
    service_cost_id: int = Field()


@router.get()
async def route(schema: PromocodeCheckSchema = Depends()):
    result = await PromocodeService().check(
        session=schema.session,
        id_str=schema.id_str,
        currency_id_str=schema.currency_cost_id,
        service_cost_id=schema.service_cost_id,
    )
    return Response(**result)
