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


from app.db.models import Currency, Service, Session
from app.repositories import CurrencyRepository, ServiceCostRepository, ServiceRepository
from app.services.base import BaseService
from app.utils.decorators import session_required


class ServiceCostService(BaseService):

    @session_required(permissions=['services'])
    async def create_by_admin(
            self,
            session: Session,
            service_id_str: str,
            currency_id_str: str,
            cost: float,
    ):
        service: Service = await ServiceRepository().get_by_id_str(id_str=service_id_str)
        currency: Currency = await CurrencyRepository().get_by_id_str(id_str=currency_id_str)
        service_cost = await ServiceCostRepository().create(
            service=service,
            currency=currency,
            cost=cost,
        )

        await self.create_action(
            model=service_cost,
            action='create',
            parameters={
                'creator': f'session_{session.id}',
                'service': currency_id_str,
                'currency': currency_id_str,
                'cost': cost,
                'by_admin': True,
            },
        )
        return {'id': service_cost.id}

    @session_required(permissions=['services'])
    async def update_by_admin(
            self,
            session: Session,
            id_: int,
            cost: float,
    ):
        service_cost = await ServiceCostRepository().get_by_id(id_=id_)

        await ServiceCostRepository().update(
            model=service_cost,
            cost=cost,
        )

        await self.create_action(
            model=service_cost,
            action='update',
            parameters={
                'updater': f'session_{session.id}',
                'cost': cost,
                'by_admin': True,
            },
        )
        return {}

    @session_required(permissions=['services'])
    async def delete_by_admin(
            self,
            session: Session,
            id_: int,
    ):
        service_cost = await ServiceCostRepository().get_by_id(id_=id_)

        await ServiceCostRepository().delete(model=service_cost)

        await self.create_action(
            model=service_cost,
            action='delete',
            parameters={
                'deleter': f'session_{session.id}',
                'by_admin': True,
            },
        )
        return {}

    @staticmethod
    async def get_list_by_service(service_id_str: str):
        service: Service = await ServiceRepository().get_by_id_str(id_str=service_id_str)
        return {
            'service_costs': [
                {
                    'currency': service_cost.currency.id_str,
                    'cost': service_cost.cost
                } for service_cost in await ServiceCostRepository().get_list_by_service(service=service)
            ]
        }
