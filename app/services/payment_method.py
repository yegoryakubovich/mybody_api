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


class PaymentMethodService(BaseService):
    @session_required(permissions=['payments'], can_root=True)
    async def create_by_admin(
            self,
            session: Session,
            id_str: str,
            name: str,
    ):
        payment_method = await PaymentMethodRepository().create(
            id_str=id_str,
            name=name,
        )

        await self.create_action(
            model=payment_method,
            action='create',
            parameters={
                'creator': f'session_{session.id}',
                'id_str': id_str,
                'name': name,
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
        payment_method = await PaymentMethodRepository().get_by_id(id_=id_)
        await PaymentMethodRepository().delete(model=payment_method)

        await self.create_action(
            model=payment_method,
            action='delete',
            parameters={
                'deleter': f'session_{session.id}',
                'by_admin': True,
            }
        )

        return {}

    @staticmethod
    async def get_list():
        return {
            'payment_methods': [
                {
                    'id': payment_method.id,
                    'id_str': payment_method.id_str,
                    'name': payment_method.name,
                } for payment_method in await PaymentMethodRepository().get_list()
            ]
        }

    @staticmethod
    async def get_list_by_currency(currency_id_str: str):
        currency = await CurrencyRepository().get_by_id_str(id_str=currency_id_str)
        return {
            'payment_methods': [
                {
                    'id': pmc.payment_method.id,
                    'id_str': pmc.payment_method.id_str,
                    'name': pmc.payment_method.name,
                    'payment_method_currency_id': pmc.id,
                } for pmc in await PaymentMethodCurrencyRepository().get_list_by_currency(currency=currency)
            ]
        }
