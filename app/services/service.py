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


from json import JSONDecodeError, loads

from app.db.models import Service, Session, Text
from app.repositories import ServiceRepository, TextRepository
from app.services.text import TextService
from app.services.base import BaseService
from app.utils import ApiException
from app.utils.decorators import session_required


class InvalidQuestionList(ApiException):
    pass


class ServiceService(BaseService):
    async def check_questions(self, questions: str):
        if not await self._is_valid_questions(questions=questions):
            raise InvalidQuestionList('Invalid question list')

    @session_required(permissions=['services'])
    async def create(
            self,
            session: Session,
            id_str: str,
            name: str,
            questions: str = None,
    ) -> dict:
        action_parameters = {
            'creator': f'session_{session.id}',
            'id_str': id_str,
            'name': name,
        }
        if questions:
            action_parameters.update(
                {
                    'questions': questions,
                }
            )
            await self.check_questions(questions=questions)
        name_text_key = f'service_{id_str}'
        name_text = await TextService().create(
            session=session,
            key=name_text_key,
            value_default=name,
            return_model=True,
        )
        service = await ServiceRepository().create(
            id_str=id_str,
            name_text=name_text,
            questions=questions,
        )

        await self.create_action(
            model=service,
            action='create',
            parameters=action_parameters,
        )
        return {
            'id': service.id,
            'id_str': service.id_str,
        }

    @session_required(permissions=['services'])
    async def update(
            self,
            session: Session,
            id_str: str,
            name: str = None,
            questions: str = None,
    ) -> dict:
        service: Service = await ServiceRepository().get_by_id_str(id_str=id_str)
        action_parameters = {
            'updater': f'session_{session.id}',
            'id_str': id_str,
        }
        if name:
            text: Text = await TextRepository().get_by_key(key=f'service_{id_str}')
            await TextRepository().update(
                text=text,
                value_default=name,
            )

            action_parameters.update(
                {
                    'name': name,
                }
            )
        if questions:
            await self.check_questions(questions=questions)

            action_parameters.update(
                {
                    'questions': questions,
                }
            )

        await ServiceRepository().update(
            service=service,
            name=name,
            questions=questions,
        )

        await self.create_action(
            model=service,
            action='update',
            parameters=action_parameters,
        )

        return {}

    @session_required(permissions=['services'])
    async def delete(
            self,
            session: Session,
            id_str: str,
    ) -> dict:
        service: Service = await ServiceRepository().get_by_id_str(id_str=id_str)
        await ServiceRepository().delete(model=service)
        await TextService().delete(
            session=session,
            key=f'service_{service.id_str}',
        )
        await self.create_action(
            model=service,
            action='delete',
            parameters={
                'deleter': f'session_{session.id}',
                'id_str': id_str,
            },
        )

        return {}

    @staticmethod
    async def get(id_str: str):
        service = await ServiceRepository().get_by_id_str(id_str=id_str)
        return {
            'service': {
                'id': service.id,
                'id_str': service.id_str,
                'name_text': service.name_text.key,
                'questions': service.questions,
            }
        }

    @staticmethod
    async def get_list() -> dict:
        services = {
            'services': [
                {
                    'id': service.id,
                    'id_str': service.id_str,
                    'name_text': service.name_text.key,
                    'questions': service.questions,
                }
                for service in await ServiceRepository().get_list()
            ]
        }
        return services

    @staticmethod
    async def _is_valid_questions(questions: str):
        try:
            questions = loads(questions)
            if len(questions) == 0:
                return False
            for question in questions:
                if not question['name'] or type(question['name']) != str:
                    return False
                if not question['type']:
                    return False
                if question['type'] not in ['dropdown', 'str', 'int']:
                    return False
                if question['type'] == 'dropdown':
                    if not question['values']:
                        return False
                    if type(question['values']) is not list:
                        return False
                    for value in question['values']:
                        if type(value) != str:
                            return False
            return True
        except JSONDecodeError:
            return False
        except TypeError:
            return False
        except KeyError:
            return False
