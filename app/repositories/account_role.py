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


from app.db.models import AccountRole, Account
from app.repositories.base import BaseRepository


class AccountRoleRepository(BaseRepository):
    model = AccountRole

    @staticmethod
    async def get_roles_by_account(account: Account, only_id_str=False):
        return [
            account_role.role.id_str if only_id_str else account_role.role
            for account_role in AccountRole.select().where(
                (AccountRole.account == account) & (AccountRole.is_deleted == False)
            )
        ]
