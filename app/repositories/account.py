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

from app.db.models import Account, NotificationService
from app.utils import ApiException
from config import ITEMS_PER_PAGE
from .base import BaseRepository


class AccountWithUsernameDoeNotExist(ApiException):
    pass


class AccountRepository(BaseRepository):
    model = Account

    @staticmethod
    async def get_by_username(username: str) -> Account:
        try:
            return Account.get(Account.username == username)
        except DoesNotExist:
            raise AccountWithUsernameDoeNotExist(f'Account @{username} does not exist')

    @staticmethod
    async def is_exist_by_username(username: str) -> bool:
        try:
            Account.get(Account.username == username)
            return True
        except DoesNotExist:
            return False

    @staticmethod
    async def get_notification_services(account: Account, only_names=False):
        services_active: list[NotificationService] = [
            service for service in account.notification_services if not service.is_deleted
        ]

        return [service.name for service in services_active] if only_names else services_active

    @staticmethod
    async def search(id_, username: str, page: int) -> tuple[list[Account], int]:
        if not username:
            username = ''
        if not id_:
            id_ = ''

        query = Account.select().where(
            (Account.is_deleted == False) &
            (Account.username % f'%{username}%') &
            (Account.id % f'%{id_}%')
        )

        accounts = query.limit(ITEMS_PER_PAGE).offset(ITEMS_PER_PAGE*(page-1)).order_by(Account.id).execute()
        results = query.count()
        return accounts, results
