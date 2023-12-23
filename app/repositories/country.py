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


from app.db.models import Country, Currency, Language, Text, Timezone
from .base import BaseRepository


class CountryRepository(BaseRepository):
    model = Country

    @staticmethod
    async def create(
            id_str: str,
            name_text: Text,
            language_default: Language,
            timezone_default: Timezone,
            currency_default: Currency,
    ):
        return Country.create(
            id_str=id_str,
            name_text=name_text,
            language_default=language_default,
            timezone_default=timezone_default,
            currency_default=currency_default,
        )

    @staticmethod
    async def update(
            country: Country,
            language_default: Language = None,
            timezone_default: Timezone = None,
            currency_default: Currency = None,
    ):
        if language_default:
            country.language_default = language_default
        if timezone_default:
            country.timezone_default = timezone_default
        if currency_default:
            country.currency_default = currency_default
        country.save()
