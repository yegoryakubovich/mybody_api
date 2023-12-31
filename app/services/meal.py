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


from datetime import datetime, date

from app.db.models import Session
from app.db.models.meal import Meal
from app.repositories import AccountServiceRepository, MealProductRepository, MealRepository
from app.services.base import BaseService
from app.utils import ApiException
from app.utils.decorators import session_required
from app.utils.meal_types import MealTypes


class InvalidMealType(ApiException):
    pass


class NoRequiredParameters(ApiException):
    pass


class NotEnoughPermissions(ApiException):
    pass


class MealService(BaseService):
    @session_required(permissions=['meals'])
    async def create_by_admin(
            self,
            session: Session,
            account_service_id: int,
            date_: date,
            type_: str,
    ):
        account_service = await AccountServiceRepository().get_by_id(id_=account_service_id)
        await self.check_meal_type(type_=type_)

        meal = await MealRepository().create(
            account_service=account_service,
            date=date_,
            type=type_,
        )

        await self.create_action(
            model=meal,
            action='create',
            parameters={
                'creator': f'session_{session.id}',
                'account_service': account_service_id,
                'date': date_,
                'type': type_,
                'by_admin': True,
            }
        )

        return {'id': meal.id}

    @session_required(permissions=['meals'])
    async def update_by_admin(
            self,
            session: Session,
            id_: int,
            date_: date = None,
            type_: str = None,

    ):
        meal = await MealRepository().get_by_id(id_=id_)

        action_parameters = {
                'updater': f'session_{session.id}',
                'by_admin': True,
        }

        if not date_ and not type_:
            raise NoRequiredParameters('One of the following parameters must be filled in: date, type')
        if date_:
            action_parameters.update(
                {
                    'date': date_,
                }
            )
        if type_:
            await self.check_meal_type(type_=type_)
            action_parameters.update(
                {
                    'type': type_,
                }
            )

        await MealRepository().update(
            model=meal,
            date=date_,
            type=type_,
        )

        await self.create_action(
            model=meal,
            action='update',
            parameters=action_parameters
        )

        return {}

    @session_required(permissions=['meals'])
    async def delete_by_admin(
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
                'by_admin': True,
            }
        )

        return {}

    @staticmethod
    async def _get(
            session: Session,
            id_: int,
            by_admin: bool = False,
    ):
        meal: Meal = await MealRepository().get_by_id(id_=id_)

        if meal.account_service.account != session.account and not by_admin:
            raise NotEnoughPermissions('Not enough permissions to execute')

        return {
            'meal': {
                'id': meal.id,
                'account_service': meal.account_service.id,
                'date': str(meal.date),
                'type': meal.type,
                'products': [
                    {
                        'id': meal_product.id,
                        'product': meal_product.product.id,
                        'value': meal_product.value,
                    } for meal_product in await MealProductRepository().get_list_by_meal(meal=meal)
                ]
            }
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

    @session_required()
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

    @session_required(permissions=['meals'], return_model=False)
    async def get_list_by_admin(self):
        return {
            'meals': [
                {
                    'id': meal.id,
                    'account_service': meal.account_service.id,
                    'date': str(meal.date),
                    'type': meal.type,
                    'products': [
                        {
                            'id': meal_product.id,
                            'product': meal_product.product.id,
                            'value': meal_product.value,
                        } for meal_product in await MealProductRepository().get_list_by_meal(meal=meal)
                    ]
                } for meal in await MealRepository().get_list()
            ]
        }

    @session_required()
    async def get_list(
            self,
            session: Session,
            account_service_id: int,
            date_: str = None,
    ):
        if date_:
            date_ = datetime.strptime(date_, '%d.%m.%y').date()
        account_service = await AccountServiceRepository().get_by_id(id_=account_service_id)
        meals = await MealRepository().get_list_by_account_service(account_service=account_service, date_=date_)

        if account_service.account != session.account:
            raise NotEnoughPermissions('Not enough permissions to execute')

        return {
            'meals': [
                {
                    'id': meal.id,
                    'account_service': meal.account_service.id,
                    'date': str(meal.date),
                    'type': meal.type,
                    'products': [
                        {
                            'id': meal_product.id,
                            'product': meal_product.product.id,
                            'value': meal_product.value,
                        } for meal_product in await MealProductRepository().get_list_by_meal(meal=meal)
                    ]
                } for meal in meals
            ]
        }

    @staticmethod
    async def check_meal_type(type_: str):
        all_ = MealTypes().all()
        if type_ not in all_:
            raise InvalidMealType(f'Invalid meal type. Available: {all_}')
