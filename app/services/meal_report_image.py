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


from config import PATH_IMAGES
from . import ImageService
from .base import BaseService
from ..db.models import MealReportImage, Session
from ..repositories import ImageRepository, MealReportRepository, MealReportImageRepository
from ..utils import ApiException
from ..utils.decorators import session_required


class NotEnoughPermissions(ApiException):
    pass


class MealReportImageService(BaseService):
    async def _create(
            self,
            session: Session,
            meal_report_id: int,
            image_id_str: str,
            by_admin: bool = False,
    ):
        meal_report = await MealReportRepository().get_by_id(id_=meal_report_id)
        image = await ImageRepository().get_by_id_str(id_str=image_id_str)

        action_parameters = {
                'creator': f'session_{session.id}',
                'meal_report': meal_report_id,
                'images': image_id_str,
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

        meal_report_image = await MealReportImageRepository().create(
            meal_report=meal_report,
            image=image,
        )

        await self.create_action(
            model=meal_report_image,
            action='create',
            parameters=action_parameters,
        )

        return meal_report_image

    @session_required()
    async def create(
            self,
            session: Session,
            meal_report_id: int,
            image_id_str: str,
    ):
        meal_report_image = await self._create(
            meal_report_id=meal_report_id,
            image_id_str=image_id_str,
            session=session,
        )

        return {'id': meal_report_image.id}

    @session_required(permissions=['meals'])
    async def create_by_admin(
            self,
            session: Session,
            meal_report_id: int,
            image_id_str: str,
    ):
        meal_report_image = await self._create(
            meal_report_id=meal_report_id,
            image_id_str=image_id_str,
            session=session,
            by_admin=True,
        )

        return {'id': meal_report_image.id}

    async def _delete(
            self,
            session: Session,
            id_: int,
            by_admin: bool = False,
    ):
        meal_report_image: MealReportImage = await MealReportImageRepository().get_by_id(id_=id_)

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
            if meal_report_image.meal_report.meal.account_service.account != session.account:
                raise NotEnoughPermissions('Not enough permissions to execute')

        await MealReportImageRepository().delete(model=meal_report_image)

        if by_admin:
            await ImageService().delete_by_admin(
                session=session,
                id_str=meal_report_image.image.id_str,
            )
        else:
            await ImageService().delete(
                session=session,
                id_str=meal_report_image.image.id_str,
            )

        await self.create_action(
            model=meal_report_image,
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
        meal_report_images = await MealReportImageRepository().get_list_by_meal_report(meal_report=meal_report)
        return [
                f'{PATH_IMAGES}/{meal_report_image.id_str}.jpg'
                for meal_report_image in meal_report_images
        ]
