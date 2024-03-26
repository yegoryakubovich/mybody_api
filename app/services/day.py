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

from app.db.models import Session, Day, Meal
from app.repositories import DayRepository, AccountServiceRepository, MealReportRepository, \
    MealProductRepository, DayMealRepository, MealRepository
from app.services.meal import MealService
from app.services.day_meal import DayMealService
from app.services.base import BaseService
from app.utils.decorators import session_required
from app.utils.exceptions import NotEnoughPermissions, ModelAlreadyExist


class DayService(BaseService):

    @session_required(permissions=['accounts'])
    async def create_by_admin(
            self,
            session: Session,
            account_service_id: int,
            date_: date,
            water_amount: int,
            return_model: bool = False,
    ):
        account_service = await AccountServiceRepository().get_by_id(id_=account_service_id)

        action_parameters = {
            'creator': f'session_{session.id}',
            'account_service_id': account_service_id,
            'date': date_,
            'by_admin': True,
        }

        day = await DayRepository().create(
            account_service=account_service,
            date=date_,
            water_amount=water_amount,
        )

        await self.create_action(
            model=day,
            action='create',
            parameters=action_parameters,
        )

        if return_model:
            return day

        return {'id': day.id}

    @session_required(permissions=['accounts'])
    async def update_by_admin(
            self,
            session: Session,
            id_: int,
            water_amount: int,
    ):
        day = await DayRepository().get_by_id(id_=id_)

        action_parameters = {
            'updater': f'session_{session.id}',
            'water_amount': water_amount,
            'by_admin': True,
        }

        await DayRepository().update(
            model=day,
            water_amount=water_amount,
        )

        await self.create_action(
            model=day,
            action='update',
            parameters=action_parameters,
        )

        return {}

    @session_required(permissions=['accounts'])
    async def delete_by_admin(
            self,
            session: Session,
            id_: int,
    ):
        day = await DayRepository().get_by_id(id_=id_)
        await DayRepository().delete(model=day)

        await self.create_action(
            model=day,
            action='delete',
            parameters={
                'deleter': f'session_{session.id}',
                'by_admin': True,
            },
        )

        return {}

    @session_required(permissions=['accounts'])
    async def duplicate_by_admin(
            self,
            session: Session,
            id_: int,
            date_: date,
    ):
        initial_day: Day = await DayRepository().get_by_id(id_=id_)
        initial_day_meals = await DayMealRepository().get_list_by_day(day=initial_day)
        try:
            duplicated_day: Day = await self.create_by_admin(
                session=session,
                account_service_id=initial_day.account_service.id,
                date_=date_,
                water_amount=initial_day.water_amount,
                return_model=True,
            )
        except ModelAlreadyExist:
            duplicated_day: Day = await DayRepository().get_by_date(
                date_=date_,
                account_service=initial_day.account_service,
            )
            await DayService().update_by_admin(
                session=session,
                id_=duplicated_day.id,
                water_amount=initial_day.water_amount,
            )
        for initial_day_meal in initial_day_meals:
            initial_meal: Meal = initial_day_meal.meal
            try:
                meal: Meal = await MealService().create_by_admin(
                    session=session,
                    account_service_id=duplicated_day.account_service.id,
                    date_=date_,
                    type_=initial_meal.type,
                    fats=initial_meal.fats,
                    proteins=initial_meal.proteins,
                    carbohydrates=initial_meal.carbohydrates,
                    return_model=True,
                )
                await DayMealService().create_by_admin(
                    session=session,
                    day_id=duplicated_day.id,
                    meal_id=meal.id,
                )
            except ModelAlreadyExist:
                duplicated_meal: Meal = await MealRepository().get_by_parameters(
                    account_service=initial_meal.account_service,
                    date_=date_,
                    type_=initial_meal.type,
                )
                await MealService().update_by_admin(
                    session=session,
                    id_=duplicated_meal.id,
                    date_=date_,
                    type_=initial_meal.type,
                    fats=initial_meal.fats,
                    proteins=initial_meal.proteins,
                    carbohydrates=initial_meal.carbohydrates,
                )

        return {'id': duplicated_day.id}

    async def _get(
            self,
            session: Session,
            id_: int,
            by_admin: bool = False,
    ):
        day = await DayRepository().get_by_id(id_=id_)
        if day.account_service.account != session.account and not by_admin:
            raise NotEnoughPermissions()

        return {
            'day': await self._generate_day_dict(day=day)
        }

    @session_required(permissions=['accounts'])
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

    async def _get_list(
            self,
            session: Session,
            account_service_id: int,
            by_admin: bool = False,
    ):
        account_service = await AccountServiceRepository().get_by_id(id_=account_service_id)
        if account_service.account != session.account and not by_admin:
            raise NotEnoughPermissions()

        return {
            'days': [
                await self._generate_day_dict(day=day)
                for day in await DayRepository().get_list_by_account_service(account_service=account_service)
            ]
        }

    @session_required(permissions=['accounts'])
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

    @staticmethod
    async def _generate_day_dict(day: Day):
        return {
            'id': day.id,
            'account_service_id': day.account_service.id,
            'date': str(day.date),
            'water_amount': day.water_amount,
            'meals': [
                {
                    'id': day_meal.id,
                    'meal_id': day_meal.meal.id,
                    'account_service_id': day_meal.meal.account_service.id,
                    'date': str(day_meal.meal.date),
                    'type': day_meal.meal.type,
                    'fats': day_meal.meal.fats,
                    'proteins': day_meal.meal.proteins,
                    'carbohydrates': day_meal.meal.carbohydrates,
                    'meal_report_id': (await MealReportRepository().get_by_meal(meal=day_meal.meal)).id if await MealReportRepository().get_by_meal(meal=day_meal.meal) else None,
                    'products': [
                        {
                            'id': meal_product.id,
                            'product': meal_product.product.id,
                            'value': meal_product.value,
                        } for meal_product in await MealProductRepository().get_list_by_meal(meal=day_meal.meal)
                    ]
                }
                for day_meal in await DayMealRepository().get_list_by_day(day=day)
            ]
        }