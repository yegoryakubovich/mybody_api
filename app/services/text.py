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


from app.db.models import Session, Text
from app.repositories import TextRepository
from app.services.base import BaseService
from app.utils.decorators import session_required


class TextService(BaseService):
    @session_required()
    async def create(
            self,
            session: Session,
            key: str,
            value_default: str,
            return_model: bool = False
    ) -> dict | Text:
        text = await TextRepository().create(
            key=key,
            value_default=value_default,
        )
        await self.create_action(
            model=text,
            action='create',
            parameters={
                'creator': f'session_{session.id}',
                'key': key,
                'value_default': value_default,
            },
        )
        if return_model:
            return text
        return {
            'text_id': text.id,
        }

    @session_required()
    async def update(
            self,
            session: Session,
            key: str,
            value_default: str,
            new_key: str = None,
    ) -> dict:
        text = await TextRepository().get_by_key(key=key)
        await TextRepository().update(
            text=text,
            value_default=value_default,
            new_key=new_key,
        )

        action_parameters = {
            'updater': f'session_{session.id}',
            'key': key,
            'value_default': value_default,
        }
        if new_key:
            action_parameters.update(
                {
                    'new_key': new_key,
                }
            )

        await self.create_action(
            model=text,
            action='update',
            parameters=action_parameters,
        )

        return {}

    @session_required()
    async def delete(
            self,
            session: Session,
            key: str,
    ) -> dict:
        text = await TextRepository().get_by_key(key=key)
        await TextRepository().delete(
            text=text,
        )
        await self.create_action(
            model=text,
            action='delete',
            parameters={
                'deleter': f'session_{session.id}',
                'key': key,
            },
        )

        return {}
