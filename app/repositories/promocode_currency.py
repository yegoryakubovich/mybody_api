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

from app.db.models import PromocodeCurrency, Promocode
from .base import BaseRepository
from ..utils.exceptions import ModelAlreadyExist


class PromocodeCurrencyRepository(BaseRepository):
    model = PromocodeCurrency

    async def create(self, **kwargs):
        try:
            promocode = kwargs.get('promocode')
            currency = kwargs.get('currency')
            PromocodeCurrency.get(
                (PromocodeCurrency.promocode == promocode) &
                (PromocodeCurrency.currency == currency) &
                (PromocodeCurrency.is_deleted == False)
            )
            raise ModelAlreadyExist(
                kwargs={
                    'model': 'PromocodeCurrency',
                    'id_type': 'promocode, currency',
                    'id_value': [promocode.id_str, currency.id_str],
                },
            )
        except DoesNotExist:
            return await super().create(**kwargs)

    @staticmethod
    async def get_list_by_promocode(promocode: Promocode) -> list[PromocodeCurrency]:
        return PromocodeCurrency.select().where(
            (PromocodeCurrency.promocode == promocode) &
            (PromocodeCurrency.is_deleted == False)
        )

    async def create(self, **kwargs):
        try:
            promocode = kwargs.get('promocode')
            currency = kwargs.get('currency')
            PromocodeCurrency.get(
                (PromocodeCurrency.promocode == promocode) &
                (PromocodeCurrency.currency == currency) &
                (PromocodeCurrency.is_deleted == False)
            )
            raise ModelAlreadyExist(
                kwargs={
                    'model': 'PromocodeCurrency',
                    'id_type': 'promocode, currency',
                    'id_value': [promocode.id_str, currency.id_str],
                },
            )
        except DoesNotExist:
            return await super().create(**kwargs)

