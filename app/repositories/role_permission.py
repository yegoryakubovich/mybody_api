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

from app.db.models import Role, RolePermission
from app.repositories.base import BaseRepository
from app.utils.exceptions import ModelAlreadyExist


class RolePermissionRepository(BaseRepository):
    model = RolePermission

    async def create(self, **kwargs):
        try:
            permission = kwargs.get('permission')
            role = kwargs.get('role')
            RolePermission.get(
                (RolePermission.role == role) &
                (RolePermission.permission == permission) &
                (RolePermission.is_deleted == False)
            )
            raise ModelAlreadyExist(
                kwargs={
                    'model': 'RolePermission',
                    'id_type': 'role, permission',
                    'id_value': [role.id, permission.id],
                },
            )
        except DoesNotExist:
            return await super().create(**kwargs)


    @staticmethod
    async def get_permissions_by_role(role: Role, only_id_str=False) -> list[str or RolePermission]:
        return [
            role_permission.permission.id_str if only_id_str else role_permission.permission
            for role_permission in RolePermission.select().where(
                (RolePermission.role == role) &
                (RolePermission.is_deleted == False)
            )
        ]

    @staticmethod
    async def get_list_by_role(role: Role) -> list[RolePermission]:
        return RolePermission.select().where(
                (RolePermission.role == role) &
                (RolePermission.is_deleted == False)
            )
