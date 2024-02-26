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

from app.services import BillingService
from app.utils import Response, Router


router = Router(
    prefix='/update',
)


class BillingUpdateByAdminSchema(BaseModel):
    token: str = Field(min_length=32, max_length=64)
    id: int = Field()
    state: str = Field(max_length=16)


@router.post()
async def route(schema: BillingUpdateByAdminSchema):
    result = await BillingService().update_by_admin(
        token=schema.token,
        id_=schema.id,
        state=schema.state,
    )
    return Response(**result)
