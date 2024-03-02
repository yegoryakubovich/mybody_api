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


from peewee import DoesNotExist

from app.db.models import Billing, AccountService
from .base import BaseRepository


class BillingRepository(BaseRepository):
    model = Billing

    @staticmethod
    async def get_list_by_account_service(
        account_service: AccountService,
    ) -> list[Billing]:
        return Billing.select().where(
            (Billing.account_service == account_service) &
            (Billing.is_deleted == False)
        ).execute()

    @staticmethod
    async def is_account_service_have_an_unpaid_bill(
        account_service: AccountService,
    ) -> bool:
        try:
            Billing.get(
                (Billing.account_service == account_service) &
                (Billing.state == 'unpaid') &
                (Billing.is_deleted == False)
            )
            return True
        except DoesNotExist:
            return False

    @staticmethod
    async def generate_new_id() -> int:
        try:
            return Billing.select().order_by(Billing.id.desc()).get().id+1
        except DoesNotExist:
            return 1