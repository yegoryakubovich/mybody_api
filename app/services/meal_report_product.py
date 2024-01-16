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


from .base import BaseService
from ..db.models import MealReportProduct, Session
from ..repositories import ProductRepository
from ..repositories.meal_report import MealReportRepository
from ..repositories.meal_report_product import MealReportProductRepository
from app.utils.exceptions import ApiException
from ..utils.decorators import session_required


class NotEnoughPermissions(ApiException):
    pass


class MealReportProductService(BaseService):
    async def _create(
            self,
            session: Session,
            meal_report_id: int,
            product_id: int,
            value: int,
            by_admin: bool = False,
    ):
        meal_report = await MealReportRepository().get_by_id(id_=meal_report_id)
        product = await ProductRepository().get_by_id(id_=product_id)

        action_parameters = {
                'creator': f'session_{session.id}',
                'meal_report_id': meal_report_id,
                'product_id': product_id,
        }

        if by_admin:
            action_parameters.update(
                {
                    'by_admin': True,
                }
            )
        else:
            if meal_report.meal.account_service.account != session.account:
                raise NotEnoughPermissions('Not enough permissions to execute')

        meal_report_product = await MealReportProductRepository().create(
            meal_report=meal_report,
            product=product,
            value=value,
        )

        await self.create_action(
            model=meal_report_product,
            action='create',
            parameters=action_parameters,
        )

        return meal_report_product

    @session_required()
    async def create(
            self,
            session: Session,
            meal_report_id: int,
            product_id: int,
            value: int,
    ):
        meal_report_product = await self._create(
            meal_report_id=meal_report_id,
            product_id=product_id,
            session=session,
            value=value
        )

        return {'id': meal_report_product.id}

    @session_required(permissions=['meals'])
    async def create_by_admin(
            self,
            session: Session,
            meal_report_id: int,
            product_id: int,
            value: int,
    ):
        meal_report_product = await self._create(
            meal_report_id=meal_report_id,
            product_id=product_id,
            session=session,
            value=value,
            by_admin=True,
        )

        return {'id': meal_report_product.id}

    async def _delete(
            self,
            session: Session,
            id_: int,
            by_admin: bool = False,
    ):
        meal_report_product: MealReportProduct = await MealReportProductRepository().get_by_id(id_=id_)

        action_parameters = {
                'deleter': f'session_{session.id}',
                'id': id_,
        }

        if by_admin:
            action_parameters.update(
                {
                    'by_admin': True,
                }
            )
        else:
            if meal_report_product.meal_report.meal.account_service.account != session.account:
                raise NotEnoughPermissions('Not enough permissions to execute')

        await MealReportProductRepository().delete(model=meal_report_product)

        await self.create_action(
            model=meal_report_product,
            action='delete',
            parameters=action_parameters,
        )

    @session_required()
    async def delete(
            self,
            session: Session,
            id_: int,
    ):
        await self._delete(
            id_=id_,
            session=session,
        )

        return {}

    @session_required(permissions=['meals'])
    async def delete_by_admin(
            self,
            session: Session,
            id_: int,
    ):
        await self._delete(
            id_=id_,
            session=session,
            by_admin=True,
        )

        return {}

    @session_required(permissions=['meals'])
    async def get_list_by_admin(
            self,
            meal_report_id: int,
    ):
        meal_report = await MealReportRepository().get_by_id(id_=meal_report_id)
        meal_report_products = await MealReportProductRepository().get_list_by_meal_report(meal_report=meal_report)
        return {
            'meal_report_products': [
                {
                    'id': meal_report_product.id,
                    'product': meal_report_product.product,
                    'value': meal_report_product.value,
                } for meal_report_product in meal_report_products
            ]
        }
