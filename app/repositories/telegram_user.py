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


from peewee import DoesNotExist

from app.db.models import TelegramUser, TelegramUrl
from app.repositories.base import BaseRepository
from ..utils.exceptions import ModelAlreadyExist


class TelegramUserRepository(BaseRepository):
    model = TelegramUser

    async def create(self, **kwargs):
        try:
            tg_id = kwargs.get('tg_id')
            TelegramUser.get(
                (TelegramUser.tg_id == tg_id) &
                (TelegramUser.is_deleted == False)
            )
            raise ModelAlreadyExist(
                kwargs={
                    'model': 'TelegramUser',
                    'id_type': 'tg_id',
                    'id_value': tg_id,
                },
            )
        except DoesNotExist:
            return await super().create(**kwargs)

    @staticmethod
    async def get_list_by_url(url: TelegramUrl) -> list[TelegramUser]:
        return TelegramUser.select().where(
            (TelegramUser.url == url) &
            (TelegramUser.is_deleted == False)
        ).execute()
