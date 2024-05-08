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

from app.db.models import TelegramUrl
from app.repositories.base import BaseRepository
from ..utils.exceptions import ModelAlreadyExist


class TelegramUrlRepository(BaseRepository):
    model = TelegramUrl

    async def create(self, **kwargs):
        try:
            id_str = kwargs.get('id_str')
            TelegramUrl.get(
                (TelegramUrl.id_str == id_str) &
                (TelegramUrl.is_deleted == False)
            )
            raise ModelAlreadyExist(
                kwargs={
                    'model': 'TelegramUrl',
                    'id_type': 'id_str',
                    'id_value': id_str,
                },
            )
        except DoesNotExist:
            return await super().create(**kwargs)
