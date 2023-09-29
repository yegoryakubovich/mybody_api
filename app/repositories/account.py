#
# (c) 2023, Yegor Yakubovich, yegoryakubovich.com, personal@yegoryakybovich.com
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

from app.db.models import Account, Country, Language, Timezone, Currency, NotificationService, AccountParameter
from app.repositories import ParameterAccountRepository
from app.utils import ApiException


class AccountWithUsernameDoeNotExist(ApiException):
    pass


class AccountRepository:
    @staticmethod
    async def create(
            username: str,
            password_salt: str,
            password_hash: str,
            firstname: str,
            lastname: str,
            country: Country,
            language: Language,
            timezone: Timezone,
            currency: Currency,
            surname: str = None,
    ) -> Account:
        account = Account.create(
            username=username,
            password_salt=password_salt,
            password_hash=password_hash,
            firstname=firstname,
            lastname=lastname,
            surname=surname,
            country=country,
            language=language,
            timezone=timezone,
            currency=currency,
        )
        return account

    @staticmethod
    async def get_by_username(username: str) -> Account:
        try:
            return Account.get(Account.username == username)
        except DoesNotExist:
            raise AccountWithUsernameDoeNotExist(f'Account @{username} does not exist')

    @staticmethod
    async def get_parameter_by_key(account: Account, key: str) -> AccountParameter:
        parameter = ParameterAccountRepository.get_by_key(key=key)
        return AccountParameter.get(
            (AccountParameter.account == account) &
            (AccountParameter.parameter == parameter)
        )

    @staticmethod
    async def is_exist(username: str) -> bool:
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
