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


from .base import BaseService
from ..db.models import Session, Training, Exercise
from ..repositories import TrainingRepository, ExerciseRepository, TrainingExerciseRepository
from ..utils import ApiException
from ..utils.decorators import session_required


class NoRequiredParameters(ApiException):
    pass


class TrainingExerciseService(BaseService):
    @session_required()
    async def create(
            self,
            session: Session,
            training_id: int,
            exercise_id: int,
            priority: int,
            value: int,
            rest: int,
    ):
        training: Training = await TrainingRepository().get_by_id(id_=training_id)
        exercise: Exercise = await ExerciseRepository().get_by_id(id_=exercise_id)
        training_exercise = await TrainingExerciseRepository().create(
            training=training,
            exercise=exercise,
            priority=priority,
            value=value,
            rest=rest,
        )

        await self.create_action(
            model=training_exercise,
            action='create',
            parameters={
                'creator': f'session_{session.id}',
                'training_id': training_id,
                'exercise_id': exercise_id,
                'priority': priority,
                'value': value,
                'rest': rest,
            }
        )

        return {'training_exercise_id': training_exercise.id}

    @session_required()
    async def update(
            self,
            session: Session,
            id_: int,
            priority: int = None,
            value: int = None,
            rest: int = None,
    ):

        training_exercise = await TrainingExerciseRepository().get_by_id(id_=id_)

        action_parameters = {
                'updater': f'session_{session.id}',
                'id': id_,
        }
        if not priority and not value and not rest:
            raise NoRequiredParameters('One of the following parameters must be filled in: priority, value, rest')
        if priority:
            action_parameters.update(
                {
                    'priority': priority,
                }
            )
        if value:
            action_parameters.update(
                {
                    'value': value,
                }
            )
        if rest:
            action_parameters.update(
                {
                    'rest': rest,
                }
            )

        await TrainingExerciseRepository().update(
            training_exercise=training_exercise,
            priority=priority,
            value=value,
            rest=rest,
        )

        await self.create_action(
            model=training_exercise,
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
        training_exercise = await TrainingExerciseRepository().get_by_id(id_=id_)
        await TrainingExerciseRepository().delete(model=training_exercise)

        await self.create_action(
            model=training_exercise,
            action='delete',
            parameters={
                'deleter': f'session_{session.id}',
                'id': id_,
            }
        )

        return {}

    @staticmethod
    async def get_list(
            training_id: int,
    ):
        training = await TrainingRepository().get_by_id(id_=training_id)
        return {
            'training_exercises': [
                {
                    'id': training_exercise.id,
                    'exercise': training_exercise.exercise.name_text.key,
                    'priority': training_exercise.priority,
                    'value': training_exercise.value,
                    'rest': training_exercise.rest,
                } for training_exercise in await TrainingExerciseRepository().get_list_by_training(training=training)
            ]
        }
