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


from json import JSONDecodeError, loads


from peewee import DoesNotExist

from .meal_report_image import MealReportImageService
from .meal_report_product import MealReportProductService
from .base import BaseService
from app.repositories import MealReportImageRepository, MealReportProductRepository, \
    MealReportRepository, \
    MealRepository, ProductRepository
from app.utils.decorators import session_required
from ..db.models import Meal, MealReport, Session
from app.utils.exceptions import InvalidProductList, ModelAlreadyExist, NotEnoughPermissions, NoRequiredParameters


class MealReportService(BaseService):

    async def _create(
            self,
            session: Session,
            meal_id: int,
            comment: str = None,
            products: str = None,
            by_admin: bool = False,
    ) -> MealReport:
        meal: Meal = await MealRepository().get_by_id(id_=meal_id)
        if not products and not comment:
            raise NoRequiredParameters(
                kwargs={
                    'parameters': ['comment', 'products']
                }
            )
        action_parameters = {
            'creator': f'session_{session.id}',
            'meal': meal_id,
        }

        if by_admin:
            action_parameters.update(
                {
                    'by_admin': True,
                }
            )
        else:
            if meal.account_service.account != session.account:
                raise NotEnoughPermissions()

        if await MealReportRepository().is_exist_by_meal(meal=meal):
            raise ModelAlreadyExist(
                kwargs={
                    'model': 'MealReport',
                    'id_type': 'Meal',
                    'id_value': meal_id,
                }
            )

        meal_report: MealReport = await MealReportRepository().create(
            meal=meal,
            comment=comment,
        )
        if products:
            products = await self.get_products_list(products=products)
            for product in products:
                if by_admin:
                    await MealReportProductService().create_by_admin(
                        session=session,
                        meal_report_id=meal_report.id,
                        product_id=product['id'],
                        value=product['value'],
                    )
                else:
                    await MealReportProductService().create(
                        session=session,
                        meal_report_id=meal_report.id,
                        product_id=product['id'],
                        value=product['value'],
                    )

        await self.create_action(
            model=meal_report,
            action='create',
            parameters=action_parameters,
        )

        return meal_report

    @session_required()
    async def create(
            self,
            session: Session,
            meal_id: int,
            comment: str = None,
            products: str = None,
    ):
        meal_report = await self._create(
            session=session,
            meal_id=meal_id,
            comment=comment,
            products=products,
        )

        return {'id': meal_report.id}

    @session_required(permissions=['meals'])
    async def create_by_admin(
            self,
            session: Session,
            meal_id: int,
            comment: str = None,
            products: str = None,
    ):
        meal_report = await self._create(
            session=session,
            meal_id=meal_id,
            comment=comment,
            products=products,
            by_admin=True,
        )

        return {'id': meal_report.id}

    async def _delete(
            self,
            session: Session,
            id_: int,
            by_admin: bool = False,
    ):
        meal_report = await MealReportRepository().get_by_id(id_=id_)

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
            if meal_report.meal.account_service.account != session.account:
                raise NotEnoughPermissions()

        products = await MealReportProductRepository().get_list_by_meal_report(meal_report=meal_report)
        images = await MealReportImageRepository().get_list_by_meal_report(meal_report=meal_report)
        for product in products:
            if by_admin:
                await MealReportProductService().delete_by_admin(
                    session=session,
                    id_=product.id,
                )
            else:
                await MealReportProductService().delete(
                    session=session,
                    id_=product.id,
                )
        for image in images:
            if by_admin:
                await MealReportImageService().delete_by_admin(
                    session=session,
                    id_=image.id,
                )
            else:
                await MealReportImageService().delete(
                    session=session,
                    id_=image.id,
                )
        await MealReportRepository().delete(model=meal_report)

        await self.create_action(
            model=meal_report,
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
            session=session,
            id_=id_,
        )
        return {}

    @session_required(permissions=['meals'])
    async def delete_by_admin(
            self,
            session: Session,
            id_: int,
    ):
        await self._delete(
            session=session,
            id_=id_,
            by_admin=True,
        )
        return {}

    @staticmethod
    async def _get(
            session: Session,
            id_: int,
            by_admin: bool = False,
    ):
        meal_report: MealReport = await MealReportRepository().get_by_id(id_=id_)

        if meal_report.meal.account_service.account != session.account and not by_admin:
            raise NotEnoughPermissions()

        meal_report_products = await MealReportProductRepository().get_list_by_meal_report(meal_report=meal_report)
        meal_report_images = await MealReportImageRepository().get_list_by_meal_report(meal_report=meal_report)

        return {
            'meal_report': {
                'products': [
                    {
                        'meal_report_product_id': meal_report_product.id,
                        'product_id': meal_report_product.product.id,
                        'value': meal_report_product.value,
                    } for meal_report_product in meal_report_products
                ],
                'images': [
                    {
                        'id_str': meal_report_image.image.id_str,
                    } for meal_report_image in meal_report_images
                ],
                'comment': meal_report.comment,
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

    async def get_products_list(self, products: str):
        if not await self._is_valid_products(products=products):
            raise InvalidProductList()
        return loads(products)

    @staticmethod
    async def _is_valid_products(products: str):
        try:
            products = loads(products)
            if len(products) == 0:
                return False
            for product in products:
                if not product['id'] or type(product['id']) != int:
                    return False
                if not product['value'] or type(product['value']) != int:
                    return False
                await ProductRepository().get_by_id(id_=product['id'])
            return True
        except JSONDecodeError:
            return False
        except TypeError:
            return False
        except KeyError:
            return False
        except DoesNotExist:
            return False
