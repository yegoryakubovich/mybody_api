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

from app.db.models import Payment, AccountService
from .base import BaseRepository


class PaymentStates:
    CREATING = 'creating'
    WAITING = 'waiting'
    PAID = 'paid'
    EXPIRED = 'expired'
    CANCELLED = 'cancelled'

    def all(self):
        return [self.CREATING, self.WAITING, self.PAID, self.EXPIRED, self.CANCELLED]


class PaymentRepository(BaseRepository):
    model = Payment

    @staticmethod
    async def get_list_by_account_service(
        account_service: AccountService,
    ) -> list[Payment]:
        return Payment.select().where(
            (Payment.account_service == account_service) &
            (Payment.is_deleted == False)
        ).execute()

    @staticmethod
    async def get_unpaid_payments_list() -> list[Payment]:
        return Payment.select().where(
            (Payment.state == PaymentStates.WAITING) &
            (Payment.is_deleted == False)
        ).execute()

    @staticmethod
    async def is_account_service_have_an_unpaid_bill(
        account_service: AccountService,
    ) -> bool:
        try:
            Payment.get(
                (Payment.account_service == account_service) &
                (Payment.state == PaymentStates.WAITING) &
                (Payment.is_deleted == False)
            )
            return True
        except DoesNotExist:
            return False

    @staticmethod
    async def generate_new_id() -> int:
        try:
            return Payment.select().order_by(Payment.id.desc()).get().id + 1
        except DoesNotExist:
            return 1
