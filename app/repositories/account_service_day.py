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

from peewee import DoesNotExist

from app.db.models import AccountServiceDay
from .base import BaseRepository
from app.db.models import AccountService
from ..utils.exceptions import ModelAlreadyExist


class AccountServiceDayRepository(BaseRepository):
    model = AccountServiceDay

    async def create(self, **kwargs):
        try:
            account_service = kwargs.get('account_service')
            date_ = kwargs.get('date')
            AccountServiceDay.get(
                (AccountServiceDay.account_service == account_service) &
                (AccountServiceDay.date == date_) &
                (AccountServiceDay.is_deleted == False)
            )
            raise ModelAlreadyExist(
                kwargs={
                    'model': 'AccountServiceDay',
                    'id_type': 'account_service, date',
                    'id_value': [account_service.id, str(date_)],
                },
            )
        except DoesNotExist:
            return await super().create(**kwargs)

    @staticmethod
    async def get_by_date(date_: date, account_service: AccountService):
        try:
            return AccountServiceDay.get(
                (AccountServiceDay.account_service == account_service) &
                (AccountServiceDay.date == date_) &
                (AccountServiceDay.is_deleted == False)
            )
        except DoesNotExist:
            return False

    @staticmethod
    async def get_list_by_account_service(account_service: AccountService):
        return AccountServiceDay.select().where(
            (AccountServiceDay.account_service == account_service) &
            (AccountServiceDay.is_deleted == False)
        )
