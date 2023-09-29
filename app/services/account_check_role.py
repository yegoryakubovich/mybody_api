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


from app.db.models import Account
from app.repositories import AccountRoleRepository
from app.services.base import BaseService
from app.utils import ApiException


class AccountMissingRole(ApiException):
    pass


class AccountCheckRoleService(BaseService):
    @staticmethod
    async def check_role(account: Account, role_id_str: str):
        if role_id_str not in await AccountRoleRepository.get_roles_by_account(account=account, only_id_str=True):
            raise AccountMissingRole(f'Account has no "{role_id_str}" role')
