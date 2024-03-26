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


from app.db.models import Session
from app.repositories import DayRepository, TrainingRepository, DayTrainingRepository
from app.services.base import BaseService
from app.utils.decorators import session_required


class DayTrainingService(BaseService):

    @session_required(permissions=['training'])
    async def create_by_admin(
            self,
            session: Session,
            day_id: int,
            training_id: int,
    ):
        day = await DayRepository().get_by_id(id_=day_id)
        training = await TrainingRepository().get_by_id(id_=training_id)

        action_parameters = {
            'creator': f'session_{session.id}',
            'day_id': day_id,
            'training_id': training_id,
            'by_admin': True,
        }

        day_training = await DayTrainingRepository().create(
            day=day,
            training=training,
        )

        await self.create_action(
            model=day_training,
            action='create',
            parameters=action_parameters,
        )

        return {'id': day_training.id}

    @session_required(permissions=['training'])
    async def update_by_admin(
            self,
            session: Session,
            id_: int,
            day_id: int,
    ):
        day_training = await DayTrainingRepository().get_by_id(id_=id_)
        day = await DayRepository().get_by_id(id_=day_id)

        action_parameters = {
            'updater': f'session_{session.id}',
            'day_id': day_id,
            'by_admin': True,
        }

        await DayTrainingRepository().update(
            model=day_training,
            day=day,
        )

        await self.create_action(
            model=day_training,
            action='update',
            parameters=action_parameters,
        )

        return {}

    @session_required(permissions=['training'])
    async def delete_by_admin(
            self,
            session: Session,
            id_: int,
    ):
        day_training = await DayTrainingRepository().get_by_id(id_=id_)
        await DayTrainingRepository().delete(model=day_training)

        await self.create_action(
            model=day_training,
            action='delete',
            parameters={
                'deleter': f'session_{session.id}',
                'by_admin': True,
            },
        )

        return {}
