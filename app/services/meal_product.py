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
from app.utils import ApiException
from app.utils.decorators import session_required


class InvalidMealType(ApiException):
    pass


class NoRequiredParameters(ApiException):
    pass


class MealProductService(BaseService):
    @session_required(permissions=['meals'])
    async def create(
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
                'meal': meal_id,
                'product': product_id,
                'value': value,
            }
        )

        return {'id': meal.id}

    @session_required(permissions=['meals'])
    async def update(
            self,
            session: Session,
            id_: int,
            product_id: int = None,
            value: int = None,
    ):
        meal_product = await MealProductRepository().get_by_id(id_=id_)

        action_parameters = {
                'updater': f'session_{session.id}',
                'id': id_,
            }

        if not product_id and not value:
            raise NoRequiredParameters('One of the following parameters must be filled in: product_id, value')
        if product_id:
            product = await ProductRepository().get_by_id(id_=product_id)
            action_parameters.update(
                {
                    'product': product_id,
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
    async def delete(
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
                'id': id_,
            }
        )

        return {}

    @staticmethod
    async def get(id_: int):
        meal_product: MealProduct = await MealProductRepository().get_by_id(id_=id_)
        return {
            'meal_product': {
                'id': meal_product.id,
                'meal': meal_product.meal.id,
                'product': meal_product.product.id,
                'value': meal_product.value,
            }
        }

    @staticmethod
    async def get_list(meal_id: int):
        meal: Meal = await MealRepository().get_by_id(id_=meal_id)
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
