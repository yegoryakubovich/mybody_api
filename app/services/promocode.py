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

from app.db.models import Session, Promocode, ServiceCost
from app.repositories import PromocodeRepository, PromocodeCurrencyRepository, ServiceCostRepository
from config import settings
from .base import BaseService
from app.utils.decorators import session_required
from app.utils.exceptions import InvalidPromocodeType, PromocodeExpired, PromocodeIsNotAvailableForYourCurrency


class PromocodeTypes:
    PERCENT = 'percent'
    AMOUNT = 'amount'

    def all(self):
        return [self.PERCENT, self.AMOUNT]


class PromocodeService(BaseService):
    @session_required(permissions=['payments'])
    async def create_by_admin(
            self,
            session: Session,
            id_str: str,
            usage_quantity: int,
            date_from: date,
            date_to: date,
            type_: str,
    ):
        await self.check_promocode_type(type_=type_)

        action_parameters = {
            'creator': f'session_{session.id}',
            'id_str': id_str,
            'usage_quantity': usage_quantity,
            'date_from': date_from,
            'date_to': date_to,
            'by_admin': True,
        }

        promocode = await PromocodeRepository().create(
            id_str=id_str,
            usage_quantity=usage_quantity,
            remaining_quantity=usage_quantity,
            date_from=date_from,
            date_to=date_to,
            type=type_,
        )

        await self.create_action(
            model=promocode,
            action='create',
            parameters=action_parameters,
        )

        return {'id': promocode.id}

    @session_required(permissions=['payments'])
    async def delete_by_admin(
            self,
            session: Session,
            id_str: str,
    ):
        promocode = await PromocodeRepository().get_by_id_str(id_str=id_str)
        await PromocodeRepository().delete(model=promocode)

        await self.create_action(
            model=promocode,
            action='delete',
            parameters={
                'deleter': f'session_{session.id}',
                'by_admin': True,
            },
        )

        return {}

    @session_required()
    async def use(
            self,
            session: Session,
            id_str: str,
    ):
        promocode = await PromocodeRepository().get_by_id_str(id_str=id_str)

        await PromocodeRepository().update(
            model=promocode,
            remaining_quantity=promocode.remaining_quantity-1,
        )

        await self.create_action(
            model=promocode,
            action='use',
            parameters={
                'updater': f'session_{session.id}',
                'remaining_quantity': promocode.remaining_quantity-1,
                'by_admin': True,
            },
        )

    async def get(self, id_str: str):
        promocode: Promocode = await PromocodeRepository().get_by_id_str(id_str=id_str)
        return {
            'promocode': await self._generate_promocode_dict(promocode=promocode)
        }

    @session_required(permissions=['payments'], return_model=False)
    async def get_list(self):
        return {
            'promocodes': [
                await self._generate_promocode_dict(promocode=promocode)
                for promocode in await PromocodeRepository().get_list()
            ]
        }

    @session_required(return_model=False)
    async def check(
            self,
            id_str: str,
            currency_id_str: str,
            service_cost_id: int,
            return_currency: bool = False,
    ):
        if id_str == settings.secret_promo_code:
            return {
                'discount_amount': 100,
                'promocode_type': 'percent',
                'cost': 0.01,
            }

        service_cost: ServiceCost = await ServiceCostRepository().get_by_id(id_=service_cost_id)
        promocode: Promocode = await PromocodeRepository().get_by_id_str(id_str=id_str)
        now = date.today()
        if now > promocode.date_to or now < promocode.date_from:
            raise PromocodeExpired()
        if promocode.remaining_quantity <= 0:
            raise PromocodeExpired()

        promocode_currencies = await PromocodeCurrencyRepository().get_list_by_promocode(promocode=promocode)
        user_promocode_currency = None
        for promocode_currency in promocode_currencies:
            if promocode_currency.currency.id_str == currency_id_str:
                user_promocode_currency = promocode_currency

        if not user_promocode_currency:
            raise PromocodeIsNotAvailableForYourCurrency()

        if return_currency:
            return user_promocode_currency

        cost = service_cost.cost
        if promocode.type == PromocodeTypes.PERCENT:
            cost = cost - (cost / 100 * user_promocode_currency.amount)
        elif promocode.type == PromocodeTypes.AMOUNT:
            cost = cost - user_promocode_currency.amount

        return {
            'discount_amount': user_promocode_currency.amount,
            'promocode_type': promocode.type,
            'cost': cost,
        }

    @staticmethod
    async def check_promocode_type(type_: str):
        all_ = PromocodeTypes().all()
        if type_ not in all_:
            raise InvalidPromocodeType(
                kwargs={
                    'all': all_,
                },
            )

    @staticmethod
    async def _generate_promocode_dict(promocode: Promocode):
        currencies = await PromocodeCurrencyRepository().get_list_by_promocode(promocode=promocode)
        return {
            'id': promocode.id,
            'id_str': promocode.id_str,
            'usage_quantity': promocode.usage_quantity,
            'remaining_quantity': promocode.remaining_quantity,
            'date_from': str(promocode.date_from),
            'date_to': str(promocode.date_to),
            'type': promocode.type,
            'currencies': [
                {
                    'id': currency.id,
                    'currency': currency.currency.id_str,
                    'amount': currency.amount,
                } for currency in currencies
            ],
        }
