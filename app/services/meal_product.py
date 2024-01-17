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


from app.db.models import MealProduct, Session
from app.db.models.meal import Meal
from app.repositories import MealProductRepository, MealRepository, ProductRepository
from app.services.base import BaseService
from app.utils.exceptions import ApiException, NoRequiredParameters, NotEnoughPermissions
from app.utils.decorators import session_required


class InvalidMealType(ApiException):
    pass


class MealProductService(BaseService):
    @session_required(permissions=['meals'])
    async def create_by_admin(
            self,
            session: Session,
            meal_id: int,
            product_id: int,
            value: int,
    ):
        meal = await MealRepository().get_by_id(id_=meal_id)
        product = await ProductRepository().get_by_id(id_=product_id)

        meal_product = await MealProductRepository().create(
            meal=meal,
            product=product,
            value=value,
        )

        await self.create_action(
            model=meal_product,
            action='create',
            parameters={
                'creator': f'session_{session.id}',
                'meal_id': meal_id,
                'product_id': product_id,
                'value': value,
                'by_admin': True,
            }
        )

        return {'id': meal.id}

    @session_required(permissions=['meals'])
    async def update_by_admin(
            self,
            session: Session,
            id_: int,
            product_id: int = None,
            value: int = None,
    ):
        meal_product = await MealProductRepository().get_by_id(id_=id_)

        action_parameters = {
                'updater': f'session_{session.id}',
                'by_admin': True,
            }

        if not product_id and not value:
            raise NoRequiredParameters(
                kwargs={
                    'parameters': ['product_id', 'value']
                }
            )
        if product_id:
            product = await ProductRepository().get_by_id(id_=product_id)
            action_parameters.update(
                {
                    'product_id': product_id,
                }
            )
        else:
            product = None
        if value:
            action_parameters.update(
                {
                    'value': value,
                }
            )

        await MealProductRepository().update(
            model=meal_product,
            product=product,
            value=value,
        )

        await self.create_action(
            model=meal_product,
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
        meal_product = await MealProductRepository().get_by_id(id_=id_)
        await MealProductRepository().delete(model=meal_product)

        await self.create_action(
            model=meal_product,
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
        meal_product: MealProduct = await MealProductRepository().get_by_id(id_=id_)
        if session.account != meal_product.meal.account_service.account and not by_admin:
            raise NotEnoughPermissions()
        return {
            'meal_product': {
                'id': meal_product.id,
                'meal': meal_product.meal.id,
                'product': meal_product.product.id,
                'value': meal_product.value,
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

    @session_required(permissions=['meals'])
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

    @staticmethod
    async def _get_list(
            session: Session,
            meal_id: int,
            by_admin: bool = False,
    ):
        meal: Meal = await MealRepository().get_by_id(id_=meal_id)
        if session.account != meal.account_service.account and not by_admin:
            raise NotEnoughPermissions()
        return {
            'meal_products': [
                {
                    'id': meal_product.id,
                    'meal': meal_product.meal.id,
                    'product': meal_product.product.id,
                    'value': meal_product.value,
                } for meal_product in await MealProductRepository().get_list_by_meal(meal=meal)
            ]
        }

    @session_required()
    async def get_list(
            self,
            session: Session,
            meal_id: int,
    ):
        return await self._get_list(
            session=session,
            meal_id=meal_id,
        )

    @session_required()
    async def get_list_by_admin(
            self,
            session: Session,
            meal_id: int,
    ):
        return await self._get_list(
            session=session,
            meal_id=meal_id,
            by_admin=True,
        )

