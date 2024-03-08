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


from app.db.models import Session, Url
from app.repositories import UrlRepository
from app.services.base import BaseService
from app.utils.exceptions import ModelAlreadyExist, NoRequiredParameters
from app.utils.decorators import session_required


class UrlService(BaseService):
    @session_required(permissions=['urls'], can_root=True)
    async def create_by_admin(
            self,
            session: Session,
            name: str,
            redirect: str,
    ):
        if await UrlRepository().is_exist_by_name(name=name):
            raise ModelAlreadyExist(
                kwargs={
                    'model': 'Url',
                    'id_type': 'name',
                    'id_value': name,
                }
            )

        url = await UrlRepository().create(
            name=name,
            redirect=redirect,
        )

        await self.create_action(
            model=url,
            action='create',
            parameters={
                'creator': f'session_{session.id}',
                'name': name,
                'redirect': redirect,
                'by_admin': True,
            }
        )

        return {'id': url.id}

    @session_required(permissions=['url'], can_root=True)
    async def update_by_admin(
            self,
            session: Session,
            id_: int,
            name: str = None,
            redirect: str = None,
    ) -> dict:
        url: Url = await UrlRepository().get_by_id(id_=id_)

        if not name and not redirect:
            raise NoRequiredParameters(
                kwargs={
                    'parameters': ['name', 'redirect'],
                }
            )

        action_parameters = {
            'updater': f'session_{session.id}',
            'by_admin': True,
        }

        if name:
            action_parameters['name'] = name
        if redirect:
            action_parameters['redirect'] = redirect

        await UrlRepository().update(
            model=url,
            name=name,
            redirect=redirect,
        )

        await self.create_action(
            model=url,
            action='update',
            parameters=action_parameters,
        )

        return {}

    @session_required(permissions=['urls'], can_root=True)
    async def delete_by_admin(
            self,
            session: Session,
            id_: int,
    ):
        url = await UrlRepository().get_by_id(id_=id_)
        await UrlRepository().delete(model=url)

        await self.create_action(
            model=url,
            action='delete',
            parameters={
                'deleter': f'session_{session.id}',
                'by_admin': True,
            }
        )

        return {}

    @staticmethod
    async def get(
            id_: int,
    ):
        url = await UrlRepository().get_by_id(id_=id_)
        return {
            'url': {
                'name': url.name,
                'redirect': url.redirect,
            }
        }

    @staticmethod
    async def get_by_name(
            name: str,
    ):
        url = await UrlRepository().get_by_name(name=name)
        return {
            'url': {
                'id': url.id,
                'name': url.name,
                'redirect': url.redirect,
            }
        }

    @staticmethod
    async def get_list() -> dict:
        urls = {
            'urls': [
                {
                    'id': url.id,
                    'name': url.name,
                    'redirect': url.redirect,
                }
                for url in await UrlRepository().get_list()
            ],
        }
        return urls
