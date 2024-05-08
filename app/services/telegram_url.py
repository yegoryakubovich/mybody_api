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
from app.repositories import TelegramUrlRepository, TelegramUserRepository
from app.services.base import BaseService
from app.utils.exceptions import ModelAlreadyExist
from app.utils.decorators import session_required


class TelegramUrlService(BaseService):
    @session_required(permissions=['telegram'], can_root=True)
    async def create_by_admin(
            self,
            session: Session,
            id_str: str,
    ):
        url = await TelegramUrlRepository().create(
            id_str=id_str,
        )

        await self.create_action(
            model=url,
            action='create',
            parameters={
                'creator': f'session_{session.id}',
                'id_str': id_str,
                'by_admin': True,
            }
        )

        return {'id_str': url.id_str}

    @session_required(permissions=['telegram'], can_root=True)
    async def delete_by_admin(
            self,
            session: Session,
            id_str: str,
    ):
        url = await TelegramUrlRepository().get_by_id_str(id_str=id_str)
        await TelegramUrlRepository().delete(model=url)

        await self.create_action(
            model=url,
            action='delete',
            parameters={
                'deleter': f'session_{session.id}',
                'id_str': id_str,
                'by_admin': True,
            }
        )

        return {}

    @session_required(permissions=['telegram'], can_root=True, return_model=False)
    async def get(
            self,
            id_str: str,
    ):
        url = await TelegramUrlRepository().get_by_id_str(id_str=id_str)
        users = await TelegramUserRepository().get_list_by_url(url=url)
        return {
            'telegram_url': {
                'id': url.id,
                'id_str': url.id_str,
                'total_users': len(users),
                'users': [
                    {
                        'id': user.id,
                        'tg_id': user.tg_id,
                        'username': user.username,
                        'firstname': user.firstname,
                        'lastname': user.lastname,
                    } for user in users
                ]
            }
        }
