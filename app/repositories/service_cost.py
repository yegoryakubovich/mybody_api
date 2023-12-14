#
# (c) 2023, Yegor Yakubovich, yegoryakubovich.com, personal@yegoryakybovich.com
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


from .base import BaseRepository
from ..db.models import Currency, Service, ServiceCost


class ServiceCostRepository(BaseRepository):
    model = ServiceCost

    @staticmethod
    async def get_list_by_service(service: Service) -> list[ServiceCost]:
        return ServiceCost.select().where(
            (ServiceCost.service == service) &
            (ServiceCost.is_deleted == False)
        ).execute()

    @staticmethod
    async def create(
            service: Service,
            currency: Currency,
            cost: float,
    ):
        return ServiceCost.create(
            service=service,
            currency=currency,
            cost=cost,
        )

    @staticmethod
    async def update(
            service_cost: ServiceCost,
            cost: float,
    ):
        service_cost.cost = cost
        service_cost.save()

    @staticmethod
    async def delete(service_cost: ServiceCost):
        service_cost.is_deleted = True
        service_cost.save()
