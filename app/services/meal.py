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


from datetime import datetime

from app.db.models import Session
from app.db.models.meal import Meal
from app.repositories import AccountServiceRepository, MealRepository
from app.services.base import BaseService
from app.utils import ApiException
from app.utils.decorators import session_required
from app.utils.meal_types import MealTypes


class InvalidMealType(ApiException):
    pass


class NoRequiredParameters(ApiException):
    pass


class MealService(BaseService):
    @session_required(permissions=['meals'])
    async def create(
            self,
            session: Session,
            account_service_id: int,
            date_: str,
            type_: str,
    ):
        account_service = await AccountServiceRepository().get_by_id(id_=account_service_id)
        date_ = datetime.strptime(date_, '%d.%m.%y').date()
        await self.check_meal_type(type_=type_)

        meal = await MealRepository().create(
            account_service=account_service,
            date_=date_,
            type_=type_,
        )

        await self.create_action(
            model=meal,
            action='create',
            parameters={
                'creator': f'session_{session.id}',
                'account_service': account_service_id,
                'date': date_,
                'type': type_,
            }
        )

        return {'id': meal.id}

    @session_required(permissions=['meals'])
    async def update(
            self,
            session: Session,
            id_: int,
            date_: str = None,
            type_: str = None,
    ):
        meal = await MealRepository().get_by_id(id_=id_)

        action_parameters = {
                'updater': f'session_{session.id}',
                'id': id_,
            }

        if not date_ and not type_:
            raise NoRequiredParameters('One of the following parameters must be filled in: date, type')
        if date_:
            action_parameters.update(
                {
                    'date': date_,
                }
            )
            date_ = datetime.strptime(date_, '%d.%m.%y').date()
        if type_:
            await self.check_meal_type(type_=type_)
            action_parameters.update(
                {
                    'type': type_,
                }
            )

        await MealRepository().update(
            model=meal,
            date_=date_,
            type_=type_,
        )

        await self.create_action(
            model=meal,
            action='update',
            parameters=action_parameters
        )

        return {}

    @session_required(permissions=['meals'])
    async def delete(
            self,
            session: Session,
            id_: int,
    ):
        meal = await MealRepository().get_by_id(id_=id_)
        await MealRepository().delete(model=meal)

        await self.create_action(
            model=meal,
            action='delete',
            parameters={
                'deleter': f'session_{session.id}',
                'id': id_,
            }
        )

        return {}

    @staticmethod
    async def get(id_: int):
        meal: Meal = await MealRepository().get_by_id(id_=id_)
        return {
            'meal': {
                'id': meal.id,
                'account_service': meal.account_service.id,
                'date': str(meal.date),
                'type': meal.type,
            }
        }

    @staticmethod
    async def get_list():
        return {
            'meals': [
                {
                    'id': meal.id,
                    'account_service': meal.account_service.id,
                    'date': str(meal.date),
                    'type': meal.type,
                } for meal in await MealRepository().get_list()
            ]
        }

    @staticmethod
    async def check_meal_type(type_: str):
        all_ = MealTypes().all()
        if type_ not in all_:
            raise InvalidMealType(f'Invalid meal type. Available: {all_}')
