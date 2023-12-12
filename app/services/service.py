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


from app.db.models import Service, Session, Text
from app.repositories import ServiceRepository, TextRepository
from app.services.text import TextService
from app.services.base import BaseService
from app.utils.decorators import session_required


class ServiceService(BaseService):
    @staticmethod
    async def get_list() -> dict:
        services = {
            'services': [
                {
                    'id': service.id,
                    'id_str': service.id_str,
                    'name_text': service.name_text.value_default,
                    'questions': service.questions,
                }
                for service in await ServiceRepository().get_list()
            ]
        }
        print(services)
        return services

    @session_required()
    async def create(
            self,
            session: Session,
            id_str: str,
            name: str,
            questions: str,
    ) -> dict:
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
            parameters={
                'creator': f'session_{session.id}',
                'id_str': id_str,
                'name': name,
                'questions': questions,
            },
        )
        return {}

    @session_required()
    async def update(
            self,
            session: Session,
            id_str: str,
            name: str = None,
            questions: str = None,
    ) -> dict:
        service: Service = await ServiceRepository().get_by_id_str(id_str=id_str)
        if name:
            text: Text = await TextRepository().get_by_key(key=f'service_{id_str}')
            await TextRepository().update(
                text=text,
                value_default=name,
            )
        await ServiceRepository().update(
            service=service,
            name=name,
            questions=questions,
        )

        action_parameters = {
            'updater': f'session_{session.id}',
            'id_str': id_str,
        }
        if name:
            action_parameters.update(
                {
                    'name': name,
                }
            )
        if questions:
            action_parameters.update(
                {
                    'questions': questions,
                }
            )

        await self.create_action(
            model=service,
            action='update',
            parameters=action_parameters,
        )

        return {}

    @session_required()
    async def delete(
            self,
            session: Session,
            id_str: str,
    ) -> dict:
        service = await ServiceRepository().get_by_id_str(id_str=id_str)
        await ServiceRepository().delete(service=service)
        await self.create_action(
            model=service,
            action='delete',
            parameters={
                'deleter': f'session_{session.id}',
                'id_str': id_str,
            },
        )

        return {}
