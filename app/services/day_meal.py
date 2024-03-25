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
from app.repositories import AccountServiceDayRepository, MealRepository, DayMealRepository
from app.services.base import BaseService
from app.utils.decorators import session_required


class DayMealService(BaseService):

    @session_required(permissions=['meals'])
    async def create_by_admin(
            self,
            session: Session,
            account_service_day_id: int,
            meal_id: int,
    ):
        account_service_day = await AccountServiceDayRepository().get_by_id(id_=account_service_day_id)
        meal = await MealRepository().get_by_id(id_=meal_id)

        action_parameters = {
            'creator': f'session_{session.id}',
            'account_service_day_id': account_service_day_id,
            'meal_id': meal_id,
            'by_admin': True,
        }

        day_meal = await DayMealRepository().create(
            account_service_day=account_service_day,
            meal=meal,
        )

        await self.create_action(
            model=day_meal,
            action='create',
            parameters=action_parameters,
        )

        return {'id': day_meal.id}

    @session_required(permissions=['meals'])
    async def update_by_admin(
            self,
            session: Session,
            id_: int,
            day_id: int,
    ):
        day_meal = await DayMealRepository().get_by_id(id_=id_)
        account_service_day = await AccountServiceDayRepository().get_by_id(id_=day_id)

        action_parameters = {
            'updater': f'session_{session.id}',
            'account_service_day_id': day_id,
            'by_admin': True,
        }

        await DayMealRepository().update(
            model=day_meal,
            account_service_day=account_service_day,
        )

        await self.create_action(
            model=day_meal,
            action='update',
            parameters=action_parameters,
        )

        return {}

    @session_required(permissions=['meals'])
    async def delete_by_admin(
            self,
            session: Session,
            id_: int,
    ):
        day_meal = await DayMealRepository().get_by_id(id_=id_)
        await DayMealRepository().delete(model=day_meal)

        await self.create_action(
            model=day_meal,
            action='delete',
            parameters={
                'deleter': f'session_{session.id}',
                'by_admin': True,
            },
        )

        return {}
