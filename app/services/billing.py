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


from app.db.models import Session, Billing, AccountService, ServiceCost
from app.repositories import BillingRepository, AccountServiceRepository, ServiceCostRepository
from app.services.base import BaseService
from app.utils.decorators import session_required
from app.utils.exceptions import InvalidBillingState, UnpaidBill, NotEnoughPermissions


class BillingStates:
    UNPAID = 'unpaid'
    PAID = 'paid'
    EXPIRED = 'expired'

    def all(self):
        return [self.UNPAID, self.PAID, self.EXPIRED]


class BillingService(BaseService):
    async def _create(
            self,
            session: Session,
            account_service_id: int,
            service_cost_id: int,
            by_admin: bool = False,
    ):
        account_service: AccountService = await AccountServiceRepository().get_by_id(id_=account_service_id)
        service_cost: ServiceCost = await ServiceCostRepository().get_by_id(id_=service_cost_id)
        cost = service_cost.cost

        if account_service.account != session.account and not by_admin:
            raise NotEnoughPermissions()

        action_parameters = {
            'creator': f'session_{session.id}',
            'account_service_id': account_service_id,
            'service_cost_id': service_cost_id,
            'cost': cost,
        }

        if by_admin:
            action_parameters['by_admin'] = True
        else:
            if await BillingRepository().is_account_service_have_an_unpaid_bill(account_service=account_service):
                raise UnpaidBill()

        id_str = f'18391-1-mybody-{await BillingRepository().generate_new_id()}'

        billing = await BillingRepository().create(
            account_service=account_service,
            service_cost=service_cost,
            cost=cost,
            id_str=id_str,
            state='unpaid',
        )

        await self.create_action(
            model=billing,
            action='create',
            parameters=action_parameters,
        )

        return {'id': billing.id}

    @session_required()
    async def create(
            self,
            session: Session,
            account_service_id: int,
            service_cost_id: int,
    ):
        return await self._create(
            session=session,
            account_service_id=account_service_id,
            service_cost_id=service_cost_id,
        )

    @session_required(permissions=['billings'])
    async def create_by_admin(
            self,
            session: Session,
            account_service_id: int,
            service_cost_id: int,
    ):
        return await self._create(
            session=session,
            account_service_id=account_service_id,
            service_cost_id=service_cost_id,
            by_admin=True,
        )

    async def _update(
            self,
            session: Session,
            id_: int,
            state: str,
            by_admin: bool = False,
    ):
        billing: Billing = await BillingRepository().get_by_id(id_=id_)

        if billing.account_service.account != session.account and not by_admin:
            raise NotEnoughPermissions()

        billing_states = BillingStates().all()

        if state not in billing_states:
            raise InvalidBillingState(
                kwargs={
                    'all': billing_states,
                }
            )

        action_parameters = {
            'updater': f'session_{session.id}',
            'state': state,
        }

        if by_admin:
            action_parameters['by_admin'] = True

        await BillingRepository.update(
            model=billing,
            state=state,
        )

        await self.create_action(
            model=billing,
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

    @session_required(permissions=['billings'])
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

    @session_required(permissions=['billings'])
    async def delete_by_admin(
            self,
            session: Session,
            id_: int,
    ):
        billing: Billing = await BillingRepository().get_by_id(id_=id_)

        await BillingRepository().delete(
            model=billing
        )

        await self.create_action(
            model=billing,
            action='delete',
            parameters={
                'deleter': f'session_{session.id}',
                'by_admin': True,
            }
        )

        return {}

    @session_required(permissions=['billings'])
    async def get(self, id_: int):
        billing: Billing = await BillingRepository().get_by_id(id_=id_)
        return {
            'billing': await self._generate_billing_dict(billing=billing)
        }

    @session_required(permissions=['billings'])
    async def get_list(self, account_service_id: int):
        account_service = await AccountServiceRepository().get_by_id(id_=account_service_id)
        return {
            'exercises': [
                await self._generate_billing_dict(billing=billing)
                for billing in await BillingRepository().get_list_by_account_service(account_service=account_service)
            ]
        }

    @staticmethod
    async def _generate_billing_dict(billing: Billing):
        return {
            'id': billing.id,
            'account_service_id': billing.account_service.id,
            'service_cost': {
                'service': billing.service_cost.service,
                'currency': billing.service_cost.currency,
                'cost': billing.service_cost.cost,
            },
            'cost': billing.cost,
        }
