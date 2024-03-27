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

from app.db.models import Session, Training, TrainingReport, Day, DayTraining
from app.repositories import TrainingExerciseRepository, TrainingReportRepository, TrainingRepository, \
    AccountServiceRepository, DayRepository, DayTrainingRepository
from app.services.day_training import DayTrainingService
from app.services.base import BaseService
from app.utils.exceptions import NotEnoughPermissions, ModelAlreadyExist, ModelDoesNotExist
from app.utils.decorators import session_required


class TrainingService(BaseService):
    @session_required(permissions=['trainings'])
    async def create_by_admin(
            self,
            session: Session,
            account_service_id: int,
            date_: date,
            return_model: bool = False,
    ):
        account_service = await AccountServiceRepository().get_by_id(id_=account_service_id)

        if await TrainingRepository().is_exist_by_date_and_account_service(account_service=account_service, date_=date_):
            raise ModelAlreadyExist(
                kwargs={
                    'model': 'Training',
                    'id_type': ['account_service_id', 'date'],
                    'id_value': [account_service_id, str(date_)],
                }
            )

        training: Training = await TrainingRepository().create(
            account_service=account_service,
            date=date_,
        )

        day: Day = await DayRepository().get_by_date(
            date_=training.date,
            account_service=training.account_service,
        )

        await DayTrainingService().create_by_admin(
            session=session,
            day_id=day.id,
            training_id=training.id,
        )

        await self.create_action(
            model=training,
            action='create',
            parameters={
                'creator': f'session_{session.id}',
                'account_service_id': account_service_id,
                'date': date_,
                'by_admin': True,
            },
        )

        if return_model:
            return training

        return {'id': training.id}

    @session_required(permissions=['trainings'])
    async def update_by_admin(
            self,
            session: Session,
            id_: int,
            date_: date,
    ):
        training: Training = await TrainingRepository().get_by_id(id_=id_)

        await TrainingRepository().update(
            model=training,
            date=date_,
        )

        day: Day = await DayRepository().get_by_date(
            date_=date_,
            account_service=training.account_service,
        )

        if not day:
            raise ModelDoesNotExist(
                kwargs={
                    'model': 'Day',
                    'id_type': 'date, account_service',
                    'id_value': [date_, training.account_service.id],
                },
            )

        await DayTrainingService().create_by_admin(
            session=session,
            day_id=day.id,
            training_id=training.id,
        )

        await self.create_action(
            model=training,
            action='update',
            parameters={
                'updater': f'session_{session.id}',
                'by_admin': True,
                'date': date_,
            },
        )

        return {}

    @session_required(permissions=['trainings'])
    async def delete_by_admin(
            self,
            session: Session,
            id_: int,
    ):
        training = await TrainingRepository().get_by_id(id_=id_)
        await TrainingRepository().delete(model=training)
        day: Day = await DayRepository().get_by_date(date_=training.date, account_service=training.account_service)
        day_training: DayTraining = await DayTrainingRepository().get_by_day(day=day)
        await DayTrainingService().delete_by_admin(session=session, id_=day_training.id)

        await self.create_action(
            model=training,
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
        training: Training = await TrainingRepository().get_by_id(id_=id_)

        if training.account_service.account != session.account and not by_admin:
            raise NotEnoughPermissions()

        return {
            'training': await self._generate_training_dict(training=training)
        }

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

    async def _get_by_date(
            self,
            session: Session,
            account_service_id: int,
            date_: date,
            by_admin: bool = False,
    ):
        account_service = await AccountServiceRepository().get_by_id(id_=account_service_id)
        training: Training = await TrainingRepository().get_by_date_and_account_service(
            account_service=account_service,
            date_=date_,
        )

        if training.account_service.account != session.account and not by_admin:
            raise NotEnoughPermissions()

        return {
            'training': await self._generate_training_dict(training=training),
        }

    @session_required(permissions=['trainings'])
    async def get_by_date_by_admin(
            self,
            session: Session,
            account_service_id: int,
            date_: date,
    ):
        return await self._get_by_date(
            session=session,
            account_service_id=account_service_id,
            date_=date_,
            by_admin=True,
        )

    @session_required()
    async def get_by_date(
            self,
            session: Session,
            account_service_id: int,
            date_: date,
    ):
        return await self._get_by_date(
            session=session,
            account_service_id=account_service_id,
            date_=date_,
        )

    async def _get_list(
            self,
            session: Session,
            account_service_id: int,
            by_admin: bool = False,
    ):
        account_service = await AccountServiceRepository().get_by_id(id_=account_service_id)
        trainings = await TrainingRepository().get_list_by_account_service(account_service=account_service)

        if account_service.account != session.account and not by_admin:
            raise NotEnoughPermissions()

        return {
            'trainings': [
                await self._generate_training_dict(training=training)
                for training in trainings
            ],
        }

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

    @session_required(permissions=['trainings'])
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

    @session_required(permissions=['trainings'], return_model=False)
    async def get_list_all_by_admin(self):
        trainings = await TrainingRepository().get_list()
        return {
            'trainings': [
                await self._generate_training_dict(training=training)
                for training in trainings
            ],
        }

    @staticmethod
    async def _generate_training_dict(training: Training):
        training_report: TrainingReport = await TrainingReportRepository().get_by_training(training=training)
        return {
            'id': training.id,
            'account_service_id': training.account_service.id,
            'date': str(training.date),
            'training_report_id': training_report.id if training_report else None,
            'exercises': [
                {
                    'id': training_exercise.id,
                    'exercise': training_exercise.exercise.id,
                    'priority': training_exercise.priority,
                    'value': training_exercise.value,
                    'rest': training_exercise.rest,
                } for training_exercise in
                await TrainingExerciseRepository().get_list_by_training(training=training)
            ]
        }
