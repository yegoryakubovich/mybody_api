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
from ..db.models import Session, Training, TrainingReport
from ..repositories import TrainingReportRepository, TrainingRepository
from app.utils.exceptions import ModelAlreadyExist, NotEnoughPermissions
from ..utils.decorators import session_required


class TrainingReportService(BaseService):
    async def _create(
            self,
            session: Session,
            training_id: int,
            comment: str,
            by_admin: bool = False,
    ) -> TrainingReport:
        training: Training = await TrainingRepository().get_by_id(id_=training_id)

        action_parameters = {
            'creator': f'session_{session.id}',
            'training_id': training_id,
        }

        if by_admin:
            action_parameters.update(
                {
                    'by_admin': True,
                }
            )
        else:
            if training.account_service.account != session.account:
                raise NotEnoughPermissions()

        if await TrainingReportRepository().is_exist_by_training(training=training):
            raise ModelAlreadyExist(
                kwargs={
                    'model': 'TrainingReport',
                    'id_type': 'Training',
                    'id_value': training_id,
                }
            )

        training_report = await TrainingReportRepository().create(
            training=training,
            comment=comment,
        )

        await self.create_action(
            model=training_report,
            action='create',
            parameters=action_parameters,
        )

        return training_report

    async def _delete(
            self,
            session: Session,
            id_: int,
            by_admin: bool = False,
    ):
        training_report = await TrainingReportRepository().get_by_id(id_=id_)

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
            if training_report.training.account_service.account != session.account:
                raise NotEnoughPermissions()

        await TrainingReportRepository().delete(model=training_report)

        await self.create_action(
            model=training_report,
            action='delete',
            parameters=action_parameters,
        )

    @staticmethod
    async def _get(
            session: Session,
            id_: int,
            by_admin: bool = False,
    ):
        training_report: TrainingReport = await TrainingReportRepository().get_by_id(id_=id_)
        if not by_admin:
            if training_report.training.account_service.account != session.account:
                raise NotEnoughPermissions()

        return {
            'training_report': {
                'training_id': training_report.training.id,
                'comment': training_report.comment,
            }
        }

    @staticmethod
    async def _get_list(
            session: Session,
            by_admin: bool = False,
    ):
        trainings_reports = await TrainingReportRepository().get_list()
        if by_admin:
            return {
                'trainings_reports': [
                    {
                        'id': training_report.id,
                        'training_id': training_report.training.id,
                        'comment': training_report.comment,
                    } for training_report in trainings_reports
                ]
            }
        else:
            return {
                'trainings_reports': [
                    {
                        'id': training_report.id,
                        'training_id': training_report.training.id,
                        'comment': training_report.comment,
                    } for training_report in trainings_reports
                    if training_report.training.account_service.account == session.account
                ]
            }

    @session_required()
    async def create(
            self,
            session: Session,
            training_id: int,
            comment: str,
    ):
        training_report = await self._create(
            session=session,
            training_id=training_id,
            comment=comment,
        )
        return {'id': training_report.id}

    @session_required()
    async def delete(
            self,
            session: Session,
            id_: int,
    ):
        await self._delete(
            session=session,
            id_=id_
        )
        return {}

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
    async def get_list(
            self,
            session: Session,
    ):
        return await self._get_list(
            session=session,
        )

    @session_required(permissions=['trainings'])
    async def create_by_admin(
            self,
            session: Session,
            training_id: int,
            comment: str,
    ):
        training_report = await self._create(
            session=session,
            training_id=training_id,
            comment=comment,
            by_admin=True,
        )
        return {'id': training_report.id}

    @session_required(permissions=['trainings'])
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

    @session_required(permissions=['trainings'])
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

    @session_required(permissions=['trainings'])
    async def get_list_by_admin(
            self,
            session: Session,
    ):
        return await self._get_list(
            session=session,
            by_admin=True,
        )
