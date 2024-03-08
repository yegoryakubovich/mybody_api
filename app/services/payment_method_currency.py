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


from app.db.models import Session
from app.repositories import PaymentMethodRepository, CurrencyRepository, PaymentMethodCurrencyRepository
from app.services.base import BaseService
from app.utils.decorators import session_required


class PaymentMethodCurrencyService(BaseService):
    @session_required(permissions=['payments'], can_root=True)
    async def create_by_admin(
            self,
            session: Session,
            payment_method_id_str: str,
            currency_id_str: str,
    ):
        payment_method = await PaymentMethodRepository().get_by_id_str(id_str=payment_method_id_str)
        currency = await CurrencyRepository().get_by_id_str(id_str=currency_id_str)
        payment_method_currency = await PaymentMethodCurrencyRepository().create(
            payment_method=payment_method,
            currency=currency,
        )

        await self.create_action(
            model=payment_method_currency,
            action='create',
            parameters={
                'creator': f'session_{session.id}',
                'payment_method': payment_method_id_str,
                'currency': currency_id_str,
                'by_admin': True,
            },
        )

        return {'id': payment_method.id}

    @session_required(permissions=['payments'])
    async def delete_by_admin(
            self,
            session: Session,
            id_: int,
    ):
        payment_method_currency = await PaymentMethodCurrencyRepository().get_by_id(id_=id_)
        await PaymentMethodCurrencyRepository().delete(model=payment_method_currency)

        await self.create_action(
            model=payment_method_currency,
            action='delete',
            parameters={
                'deleter': f'session_{session.id}',
                'by_admin': True,
            }
        )

        return {}

    @staticmethod
    async def get_list():
        payment_methods_currencies = await PaymentMethodCurrencyRepository().get_list()
        currencies = set()
        for pmc in payment_methods_currencies:
            currencies.add(pmc.currency.id_str)
        return {
            'currencies': list(currencies),
        }
