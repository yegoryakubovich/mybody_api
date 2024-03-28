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

from app.db.models import MealReport, Session, Day, DayMeal
from app.db.models.meal import Meal
from app.repositories import AccountServiceRepository, MealProductRepository, MealReportRepository, \
    MealRepository, ProductRepository, DayRepository, DayMealRepository
from app.services import AccountService
from app.services.day_meal import DayMealService
from app.services.meal_product import MealProductService
from app.services.base import BaseService
from app.services.product import ProductTypes
from app.utils import Units
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
            return_model: bool = False
    ):
        account_service = await AccountServiceRepository().get_by_id(id_=account_service_id)
        await self.check_meal_type(type_=type_)

        meal = await MealRepository().create(
            account_service=account_service,
            date=date_,
            type=type_,
            fats=fats,
            carbohydrates=carbohydrates,
            proteins=proteins,
        )

        if fats > 0:
            await self._add_main_products(
                session=session,
                meal=meal,
                nutrient_type=ProductTypes.FATS,
                nutrient_amount=fats,
            )
        if proteins > 0:
            await self._add_main_products(
                session=session,
                meal=meal,
                nutrient_type=ProductTypes.PROTEINS,
                nutrient_amount=proteins,
            )
        if carbohydrates > 0:
            await self._add_main_products(
                session=session,
                meal=meal,
                nutrient_type=ProductTypes.CARBOHYDRATES,
                nutrient_amount=carbohydrates,
            )

        day: Day = await DayRepository().get_by_date(
            date_=meal.date,
            account_service=account_service,
        )

        await DayMealService().create_by_admin(
            session=session,
            day_id=day.id,
            meal_id=meal.id,
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

        if return_model:
            return meal

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
                and not type_ \
                and not fats \
                and not proteins \
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

        fats = fats if fats else meal.fats
        proteins = proteins if proteins else meal.proteins
        carbohydrates = carbohydrates if carbohydrates else meal.carbohydrates

        if fats > 0:
            await self._add_main_products(session=session, meal=meal, nutrient_type=ProductTypes.FATS,
                                          nutrient_amount=fats, is_update=True)
        if proteins > 0:
            await self._add_main_products(session=session, meal=meal, nutrient_type=ProductTypes.PROTEINS,
                                          nutrient_amount=proteins, is_update=True)
        if carbohydrates > 0:
            await self._add_main_products(session=session, meal=meal, nutrient_type=ProductTypes.CARBOHYDRATES,
                                          nutrient_amount=carbohydrates, is_update=True)

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
        day: Day = await DayRepository().get_by_date(date_=meal.date, account_service=meal.account_service)
        day_meal: DayMeal = await DayMealRepository().get_by_day_and_meal(day=day, meal=meal)
        if day_meal:
            await DayMealService().delete_by_admin(session=session, id_=day_meal.id)

        await self.create_action(
            model=meal,
            action='delete',
            parameters={
                'deleter': f'session_{session.id}',
                'by_admin': True,
            }
        )

        return {}

    @session_required(permissions=['meals'])
    async def delete_list_by_date_by_admin(
            self,
            session: Session,
            account_service_id: int,
            date_: date,
    ):
        account_service: AccountService = await AccountServiceRepository().get_by_id(id_=account_service_id)
        meals: list[Meal] = await MealRepository().get_list_by_account_service_and_date(
            account_service=account_service,
            date_=date_,
        )
        for meal in meals:
            await self.delete_by_admin(
                session=session,
                id_=meal.id,
            )

        return {}

    @session_required(permissions=['meals'])
    async def duplicate_by_admin(
            self,
            session: Session,
            id_: int,
            date_: date = None,
            type_: str = None,
    ):
        initial_meal: Meal = await MealRepository().get_by_id(id_=id_)
        initial_day: Day = await DayRepository().get_by_date(
            account_service=initial_meal.account_service,
            date_=initial_meal.date,
        )

        if type_:
            await self.check_meal_type(type_=type_)

        if not type_ and not date_:
            raise NoRequiredParameters(
                kwargs={
                    'parameters': ['date', 'type'],
                },
            )

        if date_:
            try:
                from app.services.day import DayService
                new_day: Day = await DayService().create_by_admin(
                    session=session,
                    account_service_id=initial_meal.account_service.id,
                    date_=date_,
                    water_amount=initial_day.water_amount,
                    return_model=True,
                )
            except ModelAlreadyExist:
                new_day: Day = await DayRepository().get_by_date(
                    date_=date_,
                    account_service=initial_meal.account_service,
                )
        else:
            new_day = initial_day

        try:
            duplicated_meal: Meal = await MealService().create_by_admin(
                session=session,
                account_service_id=initial_meal.account_service.id,
                date_=initial_meal.date if not date_ else date_,
                type_=initial_meal.type if not type_ else type_,
                fats=initial_meal.fats,
                proteins=initial_meal.proteins,
                carbohydrates=initial_meal.carbohydrates,
                return_model=True,
            )
            await DayMealService().create_by_admin(
                session=session,
                day_id=new_day.id,
                meal_id=duplicated_meal.id,
            )
        except ModelAlreadyExist:
            duplicated_meal: Meal = await MealRepository().get_by_parameters(
                account_service=initial_meal.account_service,
                date_=date_,
                type_=initial_meal.type if not type_ else type_,
            )
            await self.update_by_admin(
                session=session,
                id_=duplicated_meal.id,
                date_=date_,
                type_=initial_meal.type if not type_ else type_,
                fats=initial_meal.fats,
                proteins=initial_meal.proteins,
                carbohydrates=initial_meal.carbohydrates,
            )

        return {'id': duplicated_meal.id}

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
        meals = await MealRepository().get_list_by_account_service_and_date(account_service=account_service,
                                                                            date_=date_)
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
        meals = await MealRepository().get_list_by_account_service_and_date(account_service=account_service,
                                                                            date_=date_)

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

    @staticmethod
    async def _add_main_products(
            session: Session,
            meal: Meal,
            nutrient_type: str,
            nutrient_amount: int,
            is_update: bool = False,
    ):
        list_ = await MealProductRepository().get_list_by_meal(meal=meal) \
            if is_update else await ProductRepository().get_main_by_type(type_=nutrient_type)

        for object_ in list_:
            product = object_.product if is_update else object_
            if product.type != nutrient_type:
                continue
            if nutrient_type == ProductTypes.FATS:
                product_nutrient = product.fats
            elif nutrient_type == ProductTypes.PROTEINS:
                product_nutrient = product.proteins
            else:
                product_nutrient = product.carbohydrates

            if product.unit == Units.PIECES:
                if (nutrient_amount / product_nutrient) % 1 >= 0.749:
                    meal_product_value = int(nutrient_amount / product_nutrient) + 1
                elif (nutrient_amount / product_nutrient) % 1 < 0.249:
                    meal_product_value = int(nutrient_amount / product_nutrient)
                else:
                    meal_product_value = int(nutrient_amount / product_nutrient) + 0.5
            else:
                meal_product_value = int(100 * nutrient_amount / product_nutrient)

            if not is_update:
                await MealProductService().create_by_admin(
                    session=session,
                    meal_id=meal.id,
                    product_id=product.id,
                    value=meal_product_value,
                )
            else:
                await MealProductService().update_by_admin(
                    session=session,
                    id_=object_.id,
                    product_id=product.id,
                    value=meal_product_value,
                )
