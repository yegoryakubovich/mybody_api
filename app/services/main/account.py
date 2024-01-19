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


from math import ceil
from re import compile, search

from app.db.models import Account
from app.repositories import AccountRepository, CountryRepository, LanguageRepository, TimezoneRepository, \
    CurrencyRepository, TextPackRepository
from app.services.main.account_role_check_premission import AccountRoleCheckPermissionService
from app.services.base import BaseService
from app.utils.crypto import create_salt, create_hash_by_string_and_salt
from app.utils.decorators import session_required
from app.utils.exceptions import InvalidPassword, InvalidUsername, ModelAlreadyExist, WrongPassword
from config import ITEMS_PER_PAGE


class AccountService(BaseService):
    async def create(
            self,
            username: str,
            password: str,
            firstname: str,
            lastname: str,
            country_id_str: str,
            language_id_str: str,
            timezone_id_str: str,
            currency_id_str: str,
            surname: str = None,
    ) -> dict:
        if await AccountRepository.is_exist_by_username(username=username):
            raise ModelAlreadyExist(
                kwargs={
                    'model': 'Account',
                    'id_type': 'username',
                    'id_value': username,
                }
            )
        if not self.is_valid_password(password=password):
            raise InvalidPassword()
        if not self.is_valid_username(username=username):
            raise InvalidUsername()

        # Generate salt and password hash
        password_salt = await create_salt()
        password_hash = await create_hash_by_string_and_salt(string=password, salt=password_salt)

        # Get other parameters
        country, language, timezone, currency = [
            await repository().get_by_id_str(id_str=id_str)
            for repository, id_str in zip(
                [CountryRepository, LanguageRepository, TimezoneRepository, CurrencyRepository],
                [country_id_str, language_id_str, timezone_id_str, currency_id_str],
            )
        ]

        # Create account
        account = await AccountRepository().create(
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
        # Create action
        await self.create_action(
            model=account,
            action='create',
            parameters={
                'username': username,
                'firstname': firstname,
                'lastname': lastname,
                'surname': surname,
                'country': country.id_str,
                'language': language.id_str,
                'timezone': timezone.id_str,
                'currency': currency.id_str,
            },
            with_client=True,
        )
        return {'id': account.id}

    async def check_password(
            self,
            account: Account,
            password: str,
    ):
        await self._is_correct_password(account=account, password=password)

    @staticmethod
    async def check_username(
            username: str,
    ):
        if await AccountRepository.is_exist_by_username(username=username):
            raise ModelAlreadyExist(
                kwargs={
                    'model': 'Account',
                    'id_type': 'username',
                    'id_value': username,
                }
            )
        return {}

    @session_required(return_model=False, permissions=['accounts'])
    async def get_by_admin(self, id_: int) -> dict:
        account = await AccountRepository().get_by_id(id_=id_)
        permissions = await AccountRoleCheckPermissionService.get_permissions(account=account)

        return {
            'account': {
                'username': account.username,
                'firstname': account.firstname,
                'lastname': account.lastname,
                'surname': account.surname,
                'country': account.country.id_str,
                'language': account.language.id_str,
                'timezone': account.timezone.id_str,
                'currency': account.currency.id_str,
                'permissions': permissions,
            },
        }

    @session_required(return_account=True)
    async def get(self, account: Account) -> dict:
        text_pack = await TextPackRepository.get_current(language=account.language)
        permissions = await AccountRoleCheckPermissionService.get_permissions(account=account)

        return {
            'account': {
                'username': account.username,
                'firstname': account.firstname,
                'lastname': account.lastname,
                'surname': account.surname,
                'country': account.country.id_str,
                'language': account.language.id_str,
                'timezone': account.timezone.id_str,
                'currency': account.currency.id_str,
                'permissions': permissions,
                'text_pack_id': text_pack.id,
            },
        }

    @session_required(return_model=False, permissions=['accounts'])
    async def search_by_admin(self, id_, username: str, page: int) -> dict:
        accounts, results = await AccountRepository.search(id_=id_, username=username, page=page)

        accounts = [
            {
                'id': account.id,
                'username': account.username,
                'firstname': account.firstname,
                'lastname': account.lastname,
                'surname': account.surname,
                'country': account.country.id_str,
                'language': account.language.id_str,
                'timezone': account.timezone.id_str,
                'currency': account.currency.id_str,
            }
            for account in accounts
        ]

        return {
            'accounts': accounts,
            'results': results,
            'pages': ceil(results/ITEMS_PER_PAGE),
            'page': page,
            'items_per_page': ITEMS_PER_PAGE,
        }

    @staticmethod
    async def _is_correct_password(account: Account, password: str):
        if account.password_hash == await create_hash_by_string_and_salt(
                string=password,
                salt=account.password_salt,
        ):
            return True
        else:
            raise WrongPassword()

    @staticmethod
    async def is_valid_password(password: str):
        register = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{7,32}$"
        pattern = compile(register)
        if search(pattern, password):
            return True
        else:
            return False

    @staticmethod
    async def is_valid_username(username: str):
        register = "^[a-zA-Z][a-zA-Z0-9_]{7,32}$"
        pattern = compile(register)
        if search(pattern, username):
            return True
        else:
            return False