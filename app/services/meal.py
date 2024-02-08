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


from datetime import date

from app.db.models import MealReport, Session
from app.db.models.meal import Meal
from app.repositories import AccountServiceRepository, MealProductRepository, MealReportRepository, \
    MealRepository
from app.services.base import BaseService
from app.utils.decorators import session_required
from app.utils.exceptions import InvalidMealType, NoRequiredParameters, NotEnoughPermissions, ModelAlreadyExist


class MealTypes:
    @staticmethod
    def all():
        return ['meal_1', 'meal_2', 'meal_3', 'meal_4', 'meal_5']


class MealService(BaseService):
    @session_required(permissions=['meals'])
    async def create_by_admin(
            self,
            session: Session,
            account_service_id: int,
            date_: date,
            type_: str,
            fats: int,
            proteins: int,
            carbohydrates: int,
    ):
        account_service = await AccountServiceRepository().get_by_id(id_=account_service_id)
        await self.check_meal_type(type_=type_)

        if await MealRepository().is_exist_by_parameters(
            account_service=account_service,
            date_=date_,
            type_=type_,
        ):
            raise ModelAlreadyExist(
                kwargs={
                    'model': 'Meal',
                    'id_type': ['account_service_id', 'date', 'type'],
                    'id_value': [account_service.id, str(date_), type_],
                }
            )

        meal = await MealRepository().create(
            account_service=account_service,
            date=date_,
            type=type_,
            fats=fats,
            carbohydrates=carbohydrates,
            proteins=proteins,
        )

        await self.create_action(
            model=meal,
            action='create',
            parameters={
                'creator': f'session_{session.id}',
                'account_service_id': account_service_id,
                'date': date_,
                'fats': fats,
                'proteins': proteins,
                'carbohydrates': carbohydrates,
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
            fats: int = None,
            proteins: int = None,
            carbohydrates: int = None,
    ):
        meal: Meal = await MealRepository().get_by_id(id_=id_)

        action_parameters = {
                'updater': f'session_{session.id}',
                'by_admin': True,
        }

        if not date_ \
                and not type_\
                and not fats\
                and not proteins\
                and not carbohydrates:
            raise NoRequiredParameters(
                kwargs={
                    'parameters': ['data', 'type', 'fats', 'proteins', 'carbohydrates'],
                }
            )
        if type_:
            await self.check_meal_type(type_=type_)
            action_parameters.update(
                {
                    'type': type_,
                }
            )
        if date_:
            if await MealRepository().is_exist_by_parameters(
                    account_service=meal.account_service,
                    date_=date_,
                    type_=type_,
            ):
                raise ModelAlreadyExist(
                    kwargs={
                        'model': 'Meal',
                        'id_type': ['account_service_id', 'date', 'type'],
                        'id_value': [meal.account_service.id, str(date_), type_],
                    }
                )
            action_parameters.update(
                {
                    'date': date_,
                }
            )
        if fats:
            action_parameters.update(
                {
                    'fats': fats,
                }
            )
        if proteins:
            action_parameters.update(
                {
                    'proteins': proteins,
                }
            )
        if carbohydrates:
            action_parameters.update(
                {
                    'carbohydrates': carbohydrates,
                }
            )

        await MealRepository().update(
            model=meal,
            date=date_,
            type=type_,
            fats=fats,
            carbohydrates=carbohydrates,
            proteins=proteins,
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

    async def _get(
            self,
            session: Session,
            id_: int,
            by_admin: bool = False,
    ):
        meal: Meal = await MealRepository().get_by_id(id_=id_)

        if meal.account_service.account != session.account and not by_admin:
            raise NotEnoughPermissions()

        return {
            'meal': await self._generate_meal_dict(meal=meal)
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
    async def get_list_all_by_admin(self):
        return {
            'meals': [
                await self._generate_meal_dict(meal=meal)
                for meal in await MealRepository().get_list()
            ]
        }

    @session_required(permissions=['meals'], return_model=False)
    async def get_list_by_admin(
            self,
            account_service_id: int,
            date_: date = None,
    ):
        account_service = await AccountServiceRepository().get_by_id(id_=account_service_id)
        meals = await MealRepository().get_list_by_account_service_and_date(account_service=account_service, date_=date_)
        return {
            'meals': [
                await self._generate_meal_dict(meal=meal)
                for meal in meals
            ]
        }

    @session_required()
    async def get_list(
            self,
            session: Session,
            account_service_id: int,
            date_: date = None,
    ):
        account_service = await AccountServiceRepository().get_by_id(id_=account_service_id)
        meals = await MealRepository().get_list_by_account_service_and_date(account_service=account_service, date_=date_)

        if account_service.account != session.account:
            raise NotEnoughPermissions()

        return {
            'meals': [
                await self._generate_meal_dict(meal=meal)
                for meal in meals
            ]
        }

    @staticmethod
    async def _generate_meal_dict(meal: Meal):
        meal_report: MealReport = await MealReportRepository().get_by_meal(meal=meal)
        return {
            'id': meal.id,
            'account_service_id': meal.account_service.id,
            'date': str(meal.date),
            'type': meal.type,
            'fats': meal.fats,
            'proteins': meal.proteins,
            'carbohydrates': meal.carbohydrates,
            'meal_report_id': meal_report.id if meal_report else None,
            'products': [
                {
                    'id': meal_product.id,
                    'product': meal_product.product.id,
                    'value': meal_product.value,
                } for meal_product in await MealProductRepository().get_list_by_meal(meal=meal)
            ]
        }

    @staticmethod
    async def check_meal_type(type_: str):
        all_ = MealTypes().all()
        if type_ not in all_:
            raise InvalidMealType(
                kwargs={
                    'all': all_,
                },
            )
