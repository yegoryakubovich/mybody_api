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

from app.db.models import Session, Promocode, Currency
from app.repositories import PromocodeRepository, PromocodeCurrencyRepository, CurrencyRepository
from .base import BaseService
from app.utils.decorators import session_required
from app.utils.exceptions import InvalidPromocodeType, PromocodeExpired, PromocodeIsNotAvailableForYourCurrency


class PromocodeCurrencyService(BaseService):
    @session_required(permissions=['payments'])
    async def create_by_admin(
            self,
            session: Session,
            promocode_id_str: str,
            currency_id_str: str,
            amount: float,
    ):
        action_parameters = {
            'creator': f'session_{session.id}',
            'promocode': promocode_id_str,
            'currency': currency_id_str,
            'amount': amount,
            'by_admin': True,
        }

        promocode: Promocode = await PromocodeRepository().get_by_id_str(id_str=promocode_id_str)
        currency: Currency = await CurrencyRepository().get_by_id_str(id_str=currency_id_str)

        promocode_currency = await PromocodeCurrencyRepository().create(
            promocode=promocode,
            currency=currency,
            amount=amount,
        )

        await self.create_action(
            model=promocode_currency,
            action='create',
            parameters=action_parameters,
        )

        return {'id': promocode_currency.id}

    @session_required(permissions=['payments'])
    async def delete_by_admin(
            self,
            session: Session,
            id_: int,
    ):
        promocode_currency = await PromocodeCurrencyRepository().get_by_id(id_=id_)
        await PromocodeCurrencyRepository().delete(model=promocode_currency)

        await self.create_action(
            model=promocode_currency,
            action='delete',
            parameters={
                'deleter': f'session_{session.id}',
                'by_admin': True,
            },
        )

        return {}
