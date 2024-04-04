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
from app.db.models import Session, Payment, AccountService, ServiceCost, PaymentMethod, Promocode
from app.repositories import PaymentRepository, AccountServiceRepository, ServiceCostRepository, \
    PaymentMethodRepository, PaymentMethodCurrencyRepository, PromocodeRepository
from app.repositories.payment import PaymentStates
from app.services.account_service import AccountServiceStates, AccountServiceService
from app.services.base import BaseService
from app.services.promocode import PromocodeService, PromocodeTypes
from app.utils.decorators import session_required
from app.utils.exceptions import InvalidPaymentState, UnpaidBill, NotEnoughPermissions, NoRequiredParameters, \
    PaymentCantBeCancelled
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
            promocode_id_str: str = None,
    ):
        account_service: AccountService = await AccountServiceRepository().get_by_id(id_=account_service_id)
        service_cost: ServiceCost = await ServiceCostRepository().get_by_id(id_=service_cost_id)
        payment_method: PaymentMethod = await PaymentMethodRepository().get_by_id_str(id_str=payment_method_id_str)
        payment_method_currency = await PaymentMethodCurrencyRepository().get_by_id(id_=payment_method_currency_id)
        cost = service_cost.cost

        if account_service.account != session.account and not by_admin:
            raise NotEnoughPermissions()

        if await PaymentRepository().is_account_service_have_an_unpaid_bill(account_service=account_service):
            raise UnpaidBill()

        if promocode_id_str:
            if promocode_id_str == settings.secret_promo_code:
                cost = 0.01
            else:
                promocode: Promocode = await PromocodeRepository().get_by_id_str(id_str=promocode_id_str)

                user_promocode_currency = await PromocodeService().check(
                    session=session,
                    id_str=promocode_id_str,
                    currency_id_str=service_cost.currency.id_str,
                    service_cost_id=service_cost_id,
                    return_currency=True,
                )

                if promocode.type == PromocodeTypes.PERCENT:
                    cost = cost - (cost / 100 * user_promocode_currency.amount)
                elif promocode.type == PromocodeTypes.AMOUNT:
                    cost = cost - user_promocode_currency.amount

                await PromocodeService().use(
                    session=session,
                    id_str=promocode_id_str,
                )

        action_parameters = {
            'creator': f'session_{session.id}',
            'account_service_id': account_service_id,
            'service_cost_id': service_cost_id,
            'payment_method_id_str': payment_method_id_str,
            'payment_method_currency_id': payment_method_currency_id,
            'promocode': promocode_id_str,
            'cost': cost,
        }

        if by_admin:
            action_parameters['by_admin'] = True

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

        await self.create_hg(payment_id=payment.id)  # FIXME

        return {'id': payment.id}

    @session_required()
    async def create(
            self,
            session: Session,
            account_service_id: int,
            service_cost_id: int,
            payment_method_id_str: str,
            payment_method_currency_id: int,
            promocode_id_str: str = None,
    ):
        return await self._create(
            session=session,
            account_service_id=account_service_id,
            service_cost_id=service_cost_id,
            payment_method_id_str=payment_method_id_str,
            payment_method_currency_id=payment_method_currency_id,
            promocode_id_str=promocode_id_str,
        )

    @session_required(permissions=['payments'])
    async def create_by_admin(
            self,
            session: Session,
            account_service_id: int,
            service_cost_id: int,
            payment_method_id_str: str,
            payment_method_currency_id: int,
            promocode_id_str: str = None,
    ):
        return await self._create(
            session=session,
            account_service_id=account_service_id,
            service_cost_id=service_cost_id,
            by_admin=True,
            payment_method_id_str=payment_method_id_str,
            payment_method_currency_id=payment_method_currency_id,
            promocode_id_str=promocode_id_str,
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

    @session_required()
    async def update(
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
        )

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
        payment: Payment = await PaymentRepository().get_by_id(id_=id_)

        await PaymentRepository().delete(model=payment)

        await self.create_action(
            model=payment,
            action='delete',
            parameters={
                'deleter': f'session_{session.id}',
                'by_admin': True,
            }
        )

        return {}

    async def _cancel(
            self,
            session: Session,
            id_: int,
            by_admin: bool = False,
    ):
        payment: Payment = await PaymentRepository().get_by_id(id_=id_)
        if payment.account_service.account != session.account and not by_admin:
            raise NotEnoughPermissions()
        if payment.state != PaymentStates.WAITING:
            raise PaymentCantBeCancelled(
                kwargs={
                    'id': id_,
                }
            )
        if by_admin:
            await self.update_by_admin(
                session=session,
                id_=id_,
                state=PaymentStates.CANCELLED,
            )
        else:
            await self.update(
                session=session,
                id_=id_,
                state=PaymentStates.CANCELLED,
            )
        return {}

    @session_required()
    async def cancel(
            self,
            session: Session,
            id_: int,
    ):
        return await self._cancel(
            session=session,
            id_=id_,
        )

    @session_required(permissions=['payments'])
    async def cancel_by_admin(
            self,
            session: Session,
            id_: int,
    ):
        return await self._cancel(
            session=session,
            id_=id_,
            by_admin=True,
        )

    async def _get(
            self,
            session: Session,
            id_: int,
            by_admin: bool = False,
    ):
        payments: Payment = await PaymentRepository().get_by_id(id_=id_)
        if session.account != payments.account_service.account and not by_admin:
            raise NotEnoughPermissions()
        return {
            'payment': await self._generate_payment_dict(payment=payments)
        }

    @session_required()
    async def get(
            self,
            session: Session,
            id_: int,
    ):
        return await self._get(
            session=session,
            id_=id_,
        )

    @session_required(permissions=['payments'])
    async def get_by_admin(
            self,
            session: Session,
            id_: int,
    ):
        return await self._get(
            session=session,
            id_=id_,
            by_admin=True,
        )

    async def _get_list(
            self,
            session: Session,
            account_service_id: int,
            by_admin: bool = False,
    ):
        account_service = await AccountServiceRepository().get_by_id(id_=account_service_id)
        if session.account != account_service.account and not by_admin:
            raise NotEnoughPermissions()
        return {
            'payments': [
                await self._generate_payment_dict(payment=payment)
                for payment in await PaymentRepository().get_list_by_account_service(account_service=account_service)
            ]
        }

    @session_required()
    async def get_list(
            self,
            session: Session,
            account_service_id: int,
    ):
        return await self._get_list(
            session=session,
            account_service_id=account_service_id,
        )

    @session_required(permissions=['payments'])
    async def get_list_by_admin(
            self,
            session: Session,
            account_service_id: int,
    ):
        return await self._get_list(
            session=session,
            account_service_id=account_service_id,
            by_admin=True,
        )

    @staticmethod
    async def _generate_payment_dict(payment: Payment):
        return {
            'id': payment.id,
            'account_service_id': payment.account_service.id,
            'service_cost': {
                'service': payment.service_cost.service.id_str,
                'currency': payment.service_cost.currency.id_str,
                'cost': payment.service_cost.cost,
            },
            'cost': payment.cost,
            'payment_method': payment.payment_method.id_str,
            'payment_method_currency_id': payment.payment_method_currency.id,
            'state': payment.state,
            'data': payment.data,
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
        invoice_name = f'{settings.payment_hg_prefix}-{payment.id}'
        invoice_id = await api_client.invoices.create(
            token=token,
            invoice_name=invoice_name,
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
        payment_pay_data = await api_client.invoices.get_qrcode(token=token, uuid=invoice_id)
        payment_link = payment_pay_data['tinyLink']

        await self.update_by_task(
            id_=payment.id,
            state=PaymentStates.WAITING,
            data=dumps(
                {
                    'invoice_name': invoice_name,
                    'uuid': invoice_id,
                    'payment_link': payment_link,
                    'erip_id': f'{settings.payment_hg_service_provider_id}-{settings.payment_hg_service_id}-{invoice_name}',
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

                payment_invoices = await api_client.invoices.get(token=token, search_string=payment_data['invoice_name'])
                payment_invoice = payment_invoices[0]
                is_expired = datetime.fromisoformat(payment_invoice['paymentDueTerms']['dueUTC']) < datetime.utcnow()

                if payment_invoice['totalAmount'] == payment_invoice['amountPaid']:
                    await self.update_by_task(
                        id_=payment.id,
                        state=PaymentStates.PAID,
                    )
                    if payment.account_service.state == AccountServiceStates.active:
                        datetime_to = payment.account_service.datetime_to + timedelta(31)
                        datetime_to = datetime_to - timedelta(
                            hours=datetime_to.hour,
                            minutes=datetime_to.minute,
                            seconds=datetime_to.second,
                            microseconds=datetime_to.microsecond
                        )
                        await AccountServiceService().update_by_task(
                            id_=payment.account_service.id,
                            datetime_to=datetime_to,
                        )
                    else:
                        datetime_to = datetime.utcnow() + timedelta(31)
                        datetime_to = datetime_to - timedelta(
                            hours=datetime_to.hour,
                            minutes=datetime_to.minute,
                            seconds=datetime_to.second,
                            microseconds=datetime_to.microsecond
                        )
                        await AccountServiceService().update_by_task(
                            id_=payment.account_service.id,
                            datetime_from=datetime.utcnow(),
                            datetime_to=datetime_to,
                            state=AccountServiceStates.active,
                        )

                if payment.state != PaymentStates.PAID and is_expired:
                    await self.update_by_task(
                        id_=payment.id,
                        state=PaymentStates.EXPIRED,
                    )

    @staticmethod
    async def cancel_hg(
            payment: Payment,
    ):
        api_client = HutkiGroshApiClient(
            url=settings.payment_hg_url,
        )
        payment_data = loads(payment.data)
        token = await api_client.token.get(
            client_id=settings.payment_hg_client_id,
            client_secret=settings.payment_hg_client_secret,
            service_provider_id=settings.payment_hg_service_provider_id,
            service_id=settings.payment_hg_service_id,
        )
        await api_client.invoices.set_inactive(
            token=token,
            uuid=payment_data['uuid']
        )
