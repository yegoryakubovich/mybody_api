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

from app.db.models import Session, Training
from app.repositories import ArticleRepository, TrainingRepository, AccountServiceRepository
from app.services.base import BaseService
from app.utils.exceptions import ApiException
from app.utils.decorators import session_required


class NoRequiredParameters(ApiException):
    pass


class NotEnoughPermissions(ApiException):
    pass


class TrainingService(BaseService):
    @session_required(permissions=['trainings'])
    async def create_by_admin(
            self,
            session: Session,
            account_service_id: int,
            date_: date,
            article_id: int = None,
    ):
        account_service_id = await AccountServiceRepository().get_by_id(id_=account_service_id)

        action_parameters = {
            'creator': f'session_{session.id}',
            'account_service_id': account_service_id,
            'date': date_,
            'by_admin': True,
        }

        if article_id:
            article = await ArticleRepository().get_by_id(id_=article_id)
            action_parameters.update(
                {
                    'article_id': article_id,
                }
            )
        else:
            article = None

        training = await TrainingRepository().create(
            account_service=account_service_id,
            date=date_,
            article=article,
        )

        await self.create_action(
            model=training,
            action='create',
            parameters=action_parameters,
        )

        return {'id': training.id}

    @session_required(permissions=['trainings'])
    async def update_by_admin(
            self,
            session: Session,
            id_: int,
            date_: date = None,
            article_id: int = None,
    ):
        training = await TrainingRepository().get_by_id(id_=id_)

        action_parameters = {
            'updater': f'session_{session.id}',
            'by_admin': True,
        }

        if date_:
            action_parameters.update(
                {
                    'date': date_,
                }
            )

        if article_id:
            article = await ArticleRepository().get_by_id(id_=article_id)
            action_parameters.update(
                {
                    'article_id': article_id,
                }
            )
        else:
            article = None

        await TrainingRepository().update(
            model=training,
            date=date_,
            article=article,
        )

        await self.create_action(
            model=training,
            action='update',
            parameters=action_parameters,
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

        await self.create_action(
            model=training,
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
        training: Training = await TrainingRepository().get_by_id(id_=id_)

        if training.account_service.account != session.account and not by_admin:
            raise NotEnoughPermissions('Not enough permissions to execute')

        return {
            'training': {
                'id': training.id,
                'account_service': training.account_service.id,
                'date': str(training.date),
            }
        }

    @session_required(permissions=['trainings'])
    async def get_by_admin(
            self,
            session: Session,
            id_: int,
    ):
        await self._get(
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
        await self._get(
            session=session,
            id_=id_,
        )

    @session_required()
    async def get_list(
            self,
            session: Session,
            account_service_id: int,
    ):
        account_service = await AccountServiceRepository().get_by_id(id_=account_service_id)
        trainings = await TrainingRepository().get_list_by_account_service(account_service=account_service)

        if account_service.account != session.account:
            raise NotEnoughPermissions('Not enough permissions to execute')

        return {
            'trainings': [
                {
                    'id': training.id,
                    'account_service': training.account_service.id,
                    'date': str(training.date),
                } for training in trainings
            ]
        }

    @session_required(permissions=['trainings'], return_model=False)
    async def get_list_by_admin(self):
        trainings = await TrainingRepository().get_list()
        return {
            'trainings': [
                {
                    'id': training.id,
                    'account_service': training.account_service.id,
                    'date': str(training.date),
                } for training in trainings
            ]
        }

