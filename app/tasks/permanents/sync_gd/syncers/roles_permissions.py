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


from ..utils import mybody_api_client


async def sync_roles_permissions(role_id):
    role = await mybody_api_client.admin.roles.get(id_=role_id)

    permissions = await mybody_api_client.admin.permissions.get_list()
    for permission in permissions:
        if permission not in role.permissions:
            await mybody_api_client.admin.roles.permissions.create(
                role_id=role_id,
                permission=permission.id_str,
            )
