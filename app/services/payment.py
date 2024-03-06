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


from datetime import datetime, timedelta
from json import dumps, loads

from hg_api_client.routes import HutkiGroshApiClient

from app.db import db
from app.db.models import Session, Payment, AccountService, ServiceCost, PaymentMethod
from app.repositories import PaymentRepository, AccountServiceRepository, ServiceCostRepository, \
    PaymentMethodRepository, PaymentMethodCurrencyRepository
from app.repositories.payment import PaymentStates
from app.services import AccountServiceService
from app.services.account_service import AccountServiceStates
from app.services.base import BaseService
from app.utils.decorators import session_required
from app.utils.exceptions import InvalidPaymentState, UnpaidBill, NotEnoughPermissions, NoRequiredParameters
from config import settings


class PaymentService(BaseService):
    async def _create(
            self,
            session: Session,
            account_service_id: int,
            service_cost_id: int,
            payment_method_id_str: str,
            payment_method_currency_id: int,
            by_admin: bool = False,
            promo_code: str = None,
    ):
        account_service: AccountService = await AccountServiceRepository().get_by_id(id_=account_service_id)
        service_cost: ServiceCost = await ServiceCostRepository().get_by_id(id_=service_cost_id)
        payment_method: PaymentMethod = await PaymentMethodRepository().get_by_id_str(id_str=payment_method_id_str)
        payment_method_currency = await PaymentMethodCurrencyRepository().get_by_id(id_=payment_method_currency_id)
        cost = 0.01 if promo_code == settings.secret_promo_code else service_cost.cost

        if account_service.account != session.account and not by_admin:
            raise NotEnoughPermissions()

        action_parameters = {
            'creator': f'session_{session.id}',
            'account_service_id': account_service_id,
            'service_cost_id': service_cost_id,
            'payment_method_id_str': payment_method_id_str,
            'payment_method_currency_id': payment_method_currency_id,
            'cost': cost,
        }

        if by_admin:
            action_parameters['by_admin'] = True
        else:
            if await PaymentRepository().is_account_service_have_an_unpaid_bill(account_service=account_service):
                raise UnpaidBill()

        payment = await PaymentRepository().create(
            account_service=account_service,
            payment_method=payment_method,
            payment_method_currency=payment_method_currency,
            service_cost=service_cost,
            cost=cost,
            state=PaymentStates.CREATING,
        )

        await self.create_action(
            model=payment,
            action='create',
            parameters=action_parameters,
        )

        await self.create_hg(payment_id=payment.id)

        return {'id': payment.id}

    @session_required()
    async def create(
            self,
            session: Session,
            account_service_id: int,
            service_cost_id: int,
            payment_method_id_str: str,
            payment_method_currency_id: int,
            promo_code: str = None,
    ):
        return await self._create(
            session=session,
            account_service_id=account_service_id,
            service_cost_id=service_cost_id,
            payment_method_id_str=payment_method_id_str,
            payment_method_currency_id=payment_method_currency_id,
            promo_code=promo_code,
        )

    @session_required(permissions=['payments'])
    async def create_by_admin(
            self,
            session: Session,
            account_service_id: int,
            service_cost_id: int,
            payment_method_id_str: str,
            payment_method_currency_id: int,
            promo_code: str = None,
    ):
        return await self._create(
            session=session,
            account_service_id=account_service_id,
            service_cost_id=service_cost_id,
            by_admin=True,
            payment_method_id_str=payment_method_id_str,
            payment_method_currency_id=payment_method_currency_id,
            promo_code=promo_code,
        )

    async def _update(
            self,
            id_: int,
            state: str = None,
            data: str = None,
            session: Session = None,
            by_admin: bool = False,
    ):
        payment: Payment = await PaymentRepository().get_by_id(id_=id_)

        if session:
            if payment.account_service.account != session.account and not by_admin:
                raise NotEnoughPermissions()

        payment_states = PaymentStates().all()

        if state and state not in payment_states:
            raise InvalidPaymentState(
                kwargs={
                    'all': payment_states,
                }
            )

        if not state and not data:
            raise NoRequiredParameters(
                kwargs={
                    'parameters': ['state', 'data']
                }
            )

        action_parameters = {
            'updater': f'session_{session.id}' if session else 'task',
        }

        if state:
            action_parameters['state'] = state

        if data:
            action_parameters['data'] = data

        if by_admin:
            action_parameters['by_admin'] = True

        await PaymentRepository.update(
            model=payment,
            state=state,
            data=data,
        )

        await self.create_action(
            model=payment,
            action='update',
            parameters=action_parameters,
        )

        return {}

    @session_required(permissions=['payments'])
    async def update_by_admin(
            self,
            session: Session,
            id_: int,
            state: str = None,
            data: str = None,
    ):
        return await self._update(
            session=session,
            id_=id_,
            state=state,
            data=data,
            by_admin=True,
        )

    async def update_by_task(
            self,
            id_: int,
            state: str = None,
            data: str = None,
    ):
        return await self._update(
            id_=id_,
            state=state,
            data=data,
        )

    @session_required(permissions=['payments'])
    async def delete_by_admin(
            self,
            session: Session,
            id_: int,
    ):
        payments: Payment = await PaymentRepository().get_by_id(id_=id_)

        await PaymentRepository().delete(
            model=payments
        )

        await self.create_action(
            model=payments,
            action='delete',
            parameters={
                'deleter': f'session_{session.id}',
                'by_admin': True,
            }
        )

        return {}

    @session_required(permissions=['payments'])
    async def get(self, id_: int):
        payments: Payment = await PaymentRepository().get_by_id(id_=id_)
        return {
            'payment': await self._generate_payment_dict(payment=payments)
        }

    @session_required(permissions=['payments'])
    async def get_list(self, account_service_id: int):
        account_service = await AccountServiceRepository().get_by_id(id_=account_service_id)
        return {
            'payments': [
                await self._generate_payment_dict(payment=payment)
                for payment in await PaymentRepository().get_list_by_account_service(account_service=account_service)
            ]
        }

    @staticmethod
    async def _generate_payment_dict(payment: Payment):
        return {
            'id': payment.id,
            'account_service_id': payment.account_service.id,
            'service_cost': {
                'service': payment.service_cost.service,
                'currency': payment.service_cost.currency_default,
                'cost': payment.service_cost.cost,
            },
            'cost': payment.cost,
        }

    async def create_hg(
            self,
            payment_id: int,
    ):
        payment: Payment = await PaymentRepository().get_by_id(id_=payment_id)

        api_client = HutkiGroshApiClient(
            url=settings.payment_hg_url,
        )

        token = await api_client.token.get(
            client_id=settings.payment_hg_client_id,
            client_secret=settings.payment_hg_client_secret,
            service_provider_id=settings.payment_hg_service_provider_id,
            service_id=settings.payment_hg_service_id,
        )
        invoice_id = await api_client.invoices.create(
            token=token,
            invoice_name=f'mybody-test-{payment.id}',
            service_provider_id=settings.payment_hg_service_provider_id,
            service_provider_name=settings.payment_hg_service_provider_name,
            service_id=settings.payment_hg_service_id,
            service_name=settings.payment_hg_service_name,
            address_country=settings.payment_hg_address_country,
            address_line=settings.payment_hg_address_line,
            address_city=settings.payment_hg_address_city,
            full_address=settings.payment_hg_full_address,
            locality_code=settings.payment_hg_locality_code,
            store_name=settings.payment_hg_store_name,
            store_locality_name=settings.payment_hg_store_locality_name,
            store_city=settings.payment_hg_store_city,
            store_locality_city=settings.payment_hg_store_locality_city,
            terms_of_days=1,
            items=[
                {
                    'name': 'Услуга',
                    'description': 'Оплата услуги',
                    'quantity': 1,
                    'price': payment.cost,
                    'discount_percent': 0,
                    'discount_amount': 0,
                },
            ],
        )
        await api_client.invoices.set_active(token=token, uuid=invoice_id)

        await self.update_by_task(
            id_=payment.id,
            state=PaymentStates.WAITING,
            data=dumps(
                {
                    'invoice_name': f'mybody-test-{payment.id}',
                    'uuid': invoice_id,
                },
            ),
        )

    async def check_hg(self):
        with db:
            for payment in await PaymentRepository().get_unpaid_payments_list():
                payment_data = loads(payment.data)

                api_client = HutkiGroshApiClient(
                    url=settings.payment_hg_url,
                )

                token = await api_client.token.get(
                    client_id=settings.payment_hg_client_id,
                    client_secret=settings.payment_hg_client_secret,
                    service_provider_id=settings.payment_hg_service_provider_id,
                    service_id=settings.payment_hg_service_id,
                )

                payment_invoice = await api_client.invoices.get(token=token, search_string=payment_data['invoice_name'])[0]
                is_expired = datetime.fromisoformat(payment_invoice['paymentDueTerms']['dueUTC']) < datetime.utcnow()

                if payment_invoice['totalAmount'] == payment_invoice['amountPaid']:
                    await self.update_by_task(
                        id_=payment.id,
                        state=PaymentStates.PAID,
                    )
                    if payment.account_service.state == AccountServiceStates.active:
                        await AccountServiceService().update_by_task(
                            id_=payment.account_service.id,
                            datetime_to=datetime.fromisoformat(payment.account_service.datetime_to) + timedelta(31),
                        )
                    else:
                        await AccountServiceService().update_by_task(
                            id_=payment.account_service.id,
                            datetime_from=datetime.utcnow(),
                            datetime_to=datetime.utcnow() + timedelta(31),
                            state=AccountServiceStates.active,
                        )

                if payment.state != PaymentStates.PAID and is_expired:
                    await self.update_by_task(
                        id_=payment.id,
                        state=PaymentStates.EXPIRED,
                    )
