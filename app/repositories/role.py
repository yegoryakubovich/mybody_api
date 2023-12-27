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


from peewee import DoesNotExist

from app.db.models import Role, Text
from .base import BaseRepository


class RoleRepository(BaseRepository):
    model = Role

    @staticmethod
    async def create(
            name_text: Text,
    ) -> Role:
        return Role.create(
            name_text=name_text,
        )

    @staticmethod
    async def is_exist(id_str: str) -> bool:
        try:
            Role.get(Role.id_str == id_str)
            return True
        except DoesNotExist:
            return False
