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


from app.db.models import Session
from app.repositories import ExerciseRepository
from app.services.text import TextService
from app.services.base import BaseService
from app.utils import ApiException, ExerciseTypes
from app.utils.crypto import create_id_str
from app.utils.decorators import session_required


class InvalidExerciseType(ApiException):
    pass


class ExerciseService(BaseService):
    @session_required(permissions=['exercises'])
    async def create(
            self,
            session: Session,
            name: str,
            type_: str,
    ):
        await self.check_exercise_type(type_=type_)

        name_text_key = f'exercise_{await create_id_str()}'
        name_text = await TextService().create(
            session=session,
            key=name_text_key,
            value_default=name,
            return_model=True,
        )
        exercise = await ExerciseRepository().create(
            name_text=name_text,
            type_=type_,
        )

        await self.create_action(
            model=exercise,
            action='create',
            parameters={
                'creator': f'session_{session.id}',
                'name_text_id': name_text.id,
                'type': type_,
            }
        )

        return {'id': exercise.id}

    @session_required(permissions=['exercises'])
    async def update(
            self,
            session: Session,
            id_: int,
            type_: str,
    ):
        await self.check_exercise_type(type_=type_)
        exercise = await ExerciseRepository().get_by_id(id_=id_)
        await ExerciseRepository().update(exercise=exercise, type_=type_)

        await self.create_action(
            model=exercise,
            action='update',
            parameters={
                'updater': f'session_{session.id}',
                'id': id_,
                'type': type_,
            }
        )

        return {}

    @session_required(permissions=['exercises'])
    async def delete(
            self,
            session: Session,
            id_: int,
    ):
        exercise = await ExerciseRepository().get_by_id(id_=id_)
        await ExerciseRepository().delete(model=exercise)
        await TextService().delete(session=session, key=exercise.name_text.key)

        await self.create_action(
            model=exercise,
            action='delete',
            parameters={
                'deleter': f'session_{session.id}',
                'id': id_,
            }
        )

        return {}

    @staticmethod
    async def get(id_: int):
        exercise = await ExerciseRepository().get_by_id(id_=id_)
        return {
            'exercise': {
                    'id': exercise.id,
                    'name_text': exercise.name_text.key,
                    'type': exercise.type,
            }
        }

    @staticmethod
    async def get_list():
        return {
            'exercises': [
                {
                    'id': exercise.id,
                    'name_text': exercise.name_text.key,
                    'type': exercise.type,
                } for exercise in await ExerciseRepository().get_list()
            ]
        }

    @staticmethod
    async def check_exercise_type(type_: str):
        all_ = ExerciseTypes().all()
        if type_ not in all_:
            raise InvalidExerciseType(f'Invalid exercise type. Available: {all_}')
