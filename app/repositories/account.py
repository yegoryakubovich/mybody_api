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


from app.repositories.base import BaseRepository
from app.db.models import Account, Country, Language, Timezone, Currency
from app.utils import crypto


class AccountRepository(BaseRepository):
    model = Account

    async def create(
            self,
            username: str,
            password: str,
            firstname: str,
            lastname: str,
            country: Country,
            language: Language,
            timezone: Timezone,
            currency: Currency,
            surname: str = None,
    ) -> Account:
        password_salt = await crypto.create_salt()
        password = await crypto.create_md5_by_str_and_salt(string=password, salt=password_salt)

        account = Account.create(
            username=username,
            password=password,
            password_salt=password_salt,
            firstname=firstname,
            lastname=lastname,
            surname=surname,
            country=country,
            language=language,
            timezone=timezone,
            currency=currency,
        )
        await self.create_action(
            model=account,
            action='create',
            parameters={
                'host': '0.0.0.0',
                'username': username,
                'firstname': firstname,
                'lastname': lastname,
                'surname': surname,
                'country': country.name,
                'language': language.name,
                'timezone': timezone.name,
                'currency': currency.name,
            },
        )
        return account

    @staticmethod
    async def is_exists(username: str) -> bool:
        if Account.get_or_none(Account.username == username):
            return True
        return False

    @staticmethod
    async def check_password(account: Account, password: str):
        return True if account.password == await crypto.create_md5_by_str_and_salt(
            string=password,
            salt=account.password_salt,
        ) else False
