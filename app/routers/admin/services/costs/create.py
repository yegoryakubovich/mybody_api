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

from app.services import ServiceCostService
from app.utils import Response, Router


router = Router(
    prefix='/create'
)


class ServiceCostCreateByAdminSchema(BaseModel):
    token: str = Field(min_length=32, max_length=64)
    service: str = Field(min_length=2, max_length=64)
    currency: str = Field(min_length=2, max_length=16)
    cost: float = Field()


@router.post()
async def route(schema: ServiceCostCreateByAdminSchema):
    result = await ServiceCostService().create_by_admin(
        token=schema.token,
        service_id_str=schema.service,
        currency_id_str=schema.currency,
        cost=schema.cost,
    )
    return Response(**result)
