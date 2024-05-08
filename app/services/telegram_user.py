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
from app.utils.decorators import session_required


class TelegramUserService(BaseService):
    @session_required(permissions=['telegram'], can_root=True)
    async def create_by_admin(
            self,
            session: Session,
            tg_id: int,
            firstname: str,
            url_id_str: str,
            username: str = None,
            lastname: str = None,
    ):
        url = await TelegramUrlRepository().get_by_id_str(
            id_str=url_id_str,
        )

        user = await TelegramUserRepository().create(
            tg_id=tg_id,
            username=username,
            firstname=firstname,
            lastname=lastname,
            url=url,
        )

        await self.create_action(
            model=user,
            action='create',
            parameters={
                'creator': f'session_{session.id}',
                'id': user.id,
                'by_admin': True,
            }
        )

        return {'id': user.id}
