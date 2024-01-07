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


from fastapi import UploadFile

from . import ImageService, MealReportImageService, MealReportProductService
from .base import BaseService
from app.repositories import MealReportImageRepository, MealReportProductRepository, \
    MealReportRepository, \
    MealRepository
from app.utils.decorators import session_required
from ..db.models import Meal, MealReport, Session
from ..utils import ApiException


class MealReportExist(ApiException):
    pass


class NotEnoughPermissions(ApiException):
    pass


class MealReportService(BaseService):

    async def _create(
            self,
            session: Session,
            meal_id: int,
            comment: str,
            images: list[UploadFile],
            products: list[dict],
            by_admin: bool = False,
    ) -> MealReport:
        meal: Meal = await MealRepository().get_by_id(id_=meal_id)

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
                raise NotEnoughPermissions('Not enough permissions to execute')

        if await MealReportRepository().is_exist_by_meal(meal=meal):
            raise MealReportExist(f'Report for this meal already exist')

        meal_report: MealReport = await MealReportRepository().create(
            meal=meal,
            comment=comment,
        )

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

        for file in images:
            if by_admin:
                image = await ImageService().create_by_admin(
                    session=session,
                    file=file,
                    return_model=True,
                )
                await MealReportImageService().create_by_admin(
                    session=session,
                    meal_report_id=meal_report.id,
                    image_id_str=image.id_str,
                )
            else:
                image = await ImageService().create(
                    session=session,
                    file=file,
                    return_model=True,
                )
                await MealReportImageService().create(
                    session=session,
                    meal_report_id=meal_report.id,
                    image_id_str=image.id_str,
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
            comment: str,
            images: list[UploadFile],
            products: list[dict],
    ):
        meal_report = await self._create(
            session=session,
            meal_id=meal_id,
            comment=comment,
            images=images,
            products=products,
        )

        return {'id': meal_report.id}

    @session_required(permissions=['meals'])
    async def create_by_admin(
            self,
            session: Session,
            meal_id: int,
            comment: str,
            images: list[UploadFile],
            products: list[dict],
    ):
        meal_report = await self._create(
            session=session,
            meal_id=meal_id,
            comment=comment,
            images=images,
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
                raise NotEnoughPermissions('Not enough permissions to execute')

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
            raise NotEnoughPermissions('Not enough permissions to execute')

        meal_report_products = await MealReportProductRepository().get_list_by_meal_report(meal_report=meal_report)
        meal_report_images = await MealReportImageRepository().get_list_by_meal_report(meal_report=meal_report)

        return {
            'products': [
                {
                    'id': meal_report_product.id,
                    'product': meal_report_product.product.id,
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
