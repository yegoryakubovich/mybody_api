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


from app.db.models import Permission, Text
from .base import BaseRepository


class PermissionRepository(BaseRepository):
    model = Permission

    @staticmethod
    async def create(
            id_str: str,
            name_text: Text,
    ) -> Permission:
        return Permission.create(
            id_str=id_str,
            name_text=name_text,
        )