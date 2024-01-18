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
from app.repositories import ArticleRepository, ExerciseRepository
from app.services.main.text import TextService
from app.services.base import BaseService
from app.utils.crypto import create_id_str
from app.utils.decorators import session_required
from app.utils.exceptions import InvalidExerciseType


class ExerciseTypes:
    TIME = 'time'
    QUANTITY = 'quantity'

    def all(self):
        return [self.TIME, self.QUANTITY]


class ExerciseService(BaseService):
    @session_required(permissions=['exercises'])
    async def create_by_admin(
            self,
            session: Session,
            name: str,
            type_: str,
            article_id: int = None,
    ):
        await self.check_exercise_type(type_=type_)

        name_text_key = f'exercise_{await create_id_str()}'
        name_text = await TextService().create_by_admin(
            session=session,
            key=name_text_key,
            value_default=name,
            return_model=True,
        )

        action_parameters = {
            'creator': f'session_{session.id}',
            'name_text_id': name_text.id,
            'type': type_,
            'by_admin': True,
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

        exercise = await ExerciseRepository().create(
            name_text=name_text,
            type=type_,
            article=article,
        )

        await self.create_action(
            model=exercise,
            action='create',
            parameters=action_parameters,
        )

        return {'id': exercise.id}

    @session_required(permissions=['exercises'])
    async def update_by_admin(
            self,
            session: Session,
            id_: int,
            type_: str = None,
            article_id: int = None,
    ):
        exercise = await ExerciseRepository().get_by_id(id_=id_)

        action_parameters = {
            'updater': f'session_{session.id}',
            'by_admin': True,
        }

        if article_id:
            if article_id == -1:
                article = -1
                action_parameters.update(
                    {
                        'article': None,
                    }
                )
            else:
                article = await ArticleRepository().get_by_id(id_=article_id)
                action_parameters.update(
                    {
                        'article': article_id,
                    }
                )
        else:
            article = None

        if type_:
            await self.check_exercise_type(type_=type_)
            action_parameters.update(
                {
                    'type': type_,
                }
            )

        await ExerciseRepository().update(
            model=exercise,
            type=type_,
            article=article,
        )

        await self.create_action(
            model=exercise,
            action='update',
            parameters=action_parameters,
        )

        return {}

    @session_required(permissions=['exercises'])
    async def delete_by_admin(
            self,
            session: Session,
            id_: int,
    ):
        exercise = await ExerciseRepository().get_by_id(id_=id_)
        await ExerciseRepository().delete(model=exercise)
        await TextService().delete_by_admin(session=session, key=exercise.name_text.key)

        await self.create_action(
            model=exercise,
            action='delete',
            parameters={
                'deleter': f'session_{session.id}',
                'by_admin': True,
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
            raise InvalidExerciseType(
                kwargs={
                    'all': all_,
                },
            )
