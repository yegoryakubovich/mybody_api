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


from app.models import AccountModel
from app.repositories import AccountRepository, CountryRepository, LanguageRepository, ModelDoesNotExist, \
    TimezoneRepository, CurrencyRepository
from app.utils.router import Router
from app.utils.response import Response, ResponseState


router = Router(
    prefix='/create',
)


@router.get()
async def route(account: AccountModel):
    username = account.username
    password = account.password
    firstname = account.firstname
    lastname = account.lastname
    surname = account.surname

    try:
        country, language, timezone, currency = [
            await repository().get_by_name(name=name)
            for repository, name in
            zip(
                [CountryRepository, LanguageRepository, TimezoneRepository, CurrencyRepository],
                [account.country, account.language, account.timezone, account.currency],
            )
        ]
    except ModelDoesNotExist as e:
        return Response(
            state=ResponseState.error,
            message=e.__str__(),
        )

    account_repository = AccountRepository()

    if await account_repository.is_exists(username=username):
        return Response(
            state=ResponseState.error,
            message=f'Account with username "{account.username}" already exists',
        )

    await account_repository.create(
        username=username,
        password=password,
        firstname=firstname,
        lastname=lastname,
        surname=surname,
        country=country,
        language=language,
        timezone=timezone,
        currency=currency,
    )
    return Response()
