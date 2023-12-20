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

from app.db.models import Session
from app.repositories import TrainingRepository, AccountServiceRepository
from app.services.base import BaseService
from app.utils.decorators import session_required


class TrainingService(BaseService):
    @session_required()
    async def create(
            self,
            session: Session,
            account_service_id: int,
            date_: str,
    ):
        account_service_id = await AccountServiceRepository().get_by_id(id_=account_service_id)
        training = await TrainingRepository().create(
            account_service=account_service_id,
            date_=datetime.strptime(date_, '%d.%m.%y').date(),
        )

        await self.create_action(
            model=training,
            action='create',
            parameters={
                'creator': f'session_{session.id}',
                'account_service': account_service_id,
                'date': date_,
            }
        )

        return {'training_id': training.id}

    @session_required()
    async def update(
            self,
            session: Session,
            id_: int,
            date_: str,
    ):
        training = await TrainingRepository().get_by_id(id_=id_)
        await TrainingRepository.update(
            training=training,
            date_=datetime.strptime(date_, '%d.%m.%y').date(),
        )

        await self.create_action(
            model=training,
            action='update',
            parameters={
                'updater': f'session_{session.id}',
                'id': id_,
                'date': date_,
            }
        )

        return {}

    @session_required()
    async def delete(
            self,
            session: Session,
            id_: int,
    ):
        training = await TrainingRepository().get_by_id(id_=id_)
        await TrainingRepository().delete(training=training)

        await self.create_action(
            model=training,
            action='delete',
            parameters={
                'deleter': f'session_{session.id}',
                'id': id_,
            }
        )

        return {}
