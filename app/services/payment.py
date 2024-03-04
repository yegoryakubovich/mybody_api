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


from app.db.models import Session, Payment, AccountService, ServiceCost, PaymentMethod, PaymentMethodCurrency
from app.repositories import PaymentRepository, AccountServiceRepository, ServiceCostRepository, \
    PaymentMethodRepository, PaymentMethodCurrencyRepository
from app.services.base import BaseService
from app.utils.decorators import session_required
from app.utils.exceptions import InvalidPaymentState, UnpaidBill, NotEnoughPermissions


class PaymentStates:
    CREATING = 'creating'
    WAITING = 'waiting'
    PAID = 'paid'
    EXPIRED = 'expired'

    def all(self):
        return [self.WAITING, self.PAID, self.EXPIRED]


class PaymentService(BaseService):
    async def _create(
            self,
            session: Session,
            account_service_id: int,
            service_cost_id: int,
            payment_method_id_str: str,
            payment_method_currency_id: int,
            by_admin: bool = False,
    ):
        account_service: AccountService = await AccountServiceRepository().get_by_id(id_=account_service_id)
        service_cost: ServiceCost = await ServiceCostRepository().get_by_id(id_=service_cost_id)
        payment_method: PaymentMethod = await PaymentMethodRepository().get_by_id_str(id_str=payment_method_id_str)
        payment_method_currency: PaymentMethodCurrency = await PaymentMethodCurrencyRepository().get_by_id(id_=payment_method_currency_id)
        cost = service_cost.cost

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

        return {'id': payment.id}

    @session_required()
    async def create(
            self,
            session: Session,
            account_service_id: int,
            service_cost_id: int,
            payment_method_id_str: str,
            payment_method_currency_id: int,
    ):
        return await self._create(
            session=session,
            account_service_id=account_service_id,
            service_cost_id=service_cost_id,
            payment_method_id_str=payment_method_id_str,
            payment_method_currency_id=payment_method_currency_id,
        )

    @session_required(permissions=['payments'])
    async def create_by_admin(
            self,
            session: Session,
            account_service_id: int,
            service_cost_id: int,
            payment_method_id_str: str,
            payment_method_currency_id: int,
    ):
        return await self._create(
            session=session,
            account_service_id=account_service_id,
            service_cost_id=service_cost_id,
            by_admin=True,
            payment_method_id_str=payment_method_id_str,
            payment_method_currency_id=payment_method_currency_id,
        )

    async def _update(
            self,
            session: Session,
            id_: int,
            state: str,
            by_admin: bool = False,
    ):
        payment: Payment = await PaymentRepository().get_by_id(id_=id_)

        if payment.account_service.account != session.account and not by_admin:
            raise NotEnoughPermissions()

        payment_states = PaymentStates().all()

        if state not in payment_states:
            raise InvalidPaymentState(
                kwargs={
                    'all': payment_states,
                }
            )

        action_parameters = {
            'updater': f'session_{session.id}',
            'state': state,
        }

        if by_admin:
            action_parameters['by_admin'] = True

        await PaymentRepository.update(
            model=payment,
            state=state,
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
            state: str,
    ):
        return await self._update(
            session=session,
            id_=id_,
            state=state,
        )

    @session_required(permissions=['payments'])
    async def update_by_admin(
            self,
            session: Session,
            id_: int,
            state: str,
    ):
        return await self._update(
            session=session,
            id_=id_,
            state=state,
            by_admin=True,
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
        pass

    async def check_hg(
            self,
            payment_id: int,
    ):
        pass