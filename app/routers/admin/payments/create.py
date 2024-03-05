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

from app.services import PaymentService
from app.utils import Response, Router


router = Router(
    prefix='/create',
)


class PaymentCreateByAdminSchema(BaseModel):
    token: str = Field(min_length=32, max_length=64)
    account_service_id: int = Field()
    service_cost_id: int = Field()
    payment_method: str = Field(max_length=16)
    payment_method_currency_id: int = Field()
    promo_code: str | None = Field(min_length=16, default=None)


@router.post()
async def route(schema: PaymentCreateByAdminSchema):
    result = await PaymentService().create_by_admin(
        token=schema.token,
        account_service_id=schema.account_service_id,
        service_cost_id=schema.service_cost_id,
        payment_method_id_str=schema.payment_method,
        payment_method_currency_id=schema.payment_method_currency_id,
        promo_code=schema.promo_code,
    )
    return Response(**result)
