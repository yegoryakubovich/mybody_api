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


from app.services import AccountCheckRoleService
from app.services.session_get_by_token import SessionGetByTokenService


def session_required(only_account: bool = False, only_roles: list[str] = None):
    def inner(function):
        async def wrapper(*args, **kwargs):
            token = kwargs.get('token')
            kwargs.pop('token')

            session = await SessionGetByTokenService().execute(token=token)
            if only_account:
                kwargs['account'] = session.account
            else:
                kwargs['session'] = session

            if only_roles:
                for role in only_roles:
                    await AccountCheckRoleService().check_role(account=session.account, role_id_str=role)

            return await function(*args, **kwargs)
        return wrapper
    return inner
