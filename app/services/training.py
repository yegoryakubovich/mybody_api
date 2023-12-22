#
# (c) 2023, Yegor Yakubovich, yegoryakubovich.com, personal@yegoryakybovich.com
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


from datetime import datetime

from app.db.models import Session, Training
from app.repositories import ArticleRepository, TrainingRepository, AccountServiceRepository
from app.services.base import BaseService
from app.utils import ApiException
from app.utils.decorators import session_required


class NoRequiredParameters(ApiException):
    pass


class TrainingService(BaseService):
    @session_required()
    async def create(
            self,
            session: Session,
            account_service_id: int,
            date_: str,
            article_id: int = None,
    ):
        account_service_id = await AccountServiceRepository().get_by_id(id_=account_service_id)

        action_parameters = {
                'creator': f'session_{session.id}',
                'account_service': account_service_id,
                'date': date_,
        }

        if article_id:
            article = await ArticleRepository().get_by_id(id_=article_id)
            action_parameters.update(
                {
                    'article': article_id,
                }
            )
        else:
            article = None

        training = await TrainingRepository().create(
            account_service=account_service_id,
            date_=datetime.strptime(date_, '%d.%m.%y').date(),
            article=article,
        )

        await self.create_action(
            model=training,
            action='create',
            parameters=action_parameters,
        )

        return {'id': training.id}

    @session_required()
    async def update(
            self,
            session: Session,
            id_: int,
            date_: str = None,
            article_id: int = None,
    ):
        training = await TrainingRepository().get_by_id(id_=id_)

        action_parameters = {
            'updater': f'session_{session.id}',
            'id': id_,
        }

        if date_:
            action_parameters.update(
                {
                    'date': date_,
                }
            )
            date_ = datetime.strptime(date_, '%d.%m.%y').date()

        if article_id:
            article = await ArticleRepository().get_by_id(id_=article_id)
            action_parameters.update(
                {
                    'article': article_id,
                }
            )
        else:
            article = None

        await TrainingRepository.update(
            training=training,
            date_=date_,
            article=article,
        )

        await self.create_action(
            model=training,
            action='update',
            parameters=action_parameters,
        )

        return {}

    @session_required()
    async def delete(
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
                'id': id_,
            }
        )

        return {}

    @staticmethod
    async def get(id_: int):
        training: Training = await TrainingRepository().get_by_id(id_=id_)
        return {
            'training': {
                'id': training.id,
                'account_service': training.account_service.id,
                'date': training.date,
            }
        }

    @staticmethod
    async def get_list():
        return {
            'trainings': [
                {
                    'id': training.id,
                    'account_service': training.account_service.id,
                    'date': training.date,
                } for training in await TrainingRepository().get_list()
            ]
        }

