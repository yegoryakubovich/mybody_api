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


from app.repositories.account import AccountRepository
from app.repositories.base import BaseRepository
from app.db.models import Session, Account
from app.utils import ApiException
from app.utils.crypto import create_salt, create_hash_by_string_and_salt


class WrongToken(ApiException):
    pass


class SessionRepository(BaseRepository):
    model = Session

    async def create(self, account: Account, password: str) -> str:
        await AccountRepository.check_password(account=account, password=password)

        token = await create_salt()
        token_salt = await create_salt()
        token_hash = await create_hash_by_string_and_salt(string=token, salt=token_salt)

        session = Session.create(
            account=account,
            token_hash=token_hash,
            token_salt=token_salt,
        )
        await self.create_action(model=session, action='create', with_client=True)

        token = f'{session.id:08}:{token}'
        return token

    async def get_account_by_token(self, token: str):
        session_id_str, token = token.split(':')
        session_id = int(session_id_str)

        session: Session = await self.get_by_id(model_id=session_id)
        if session.token_hash == await create_hash_by_string_and_salt(
            string=token,
            salt=session.token_salt,
        ):
            return session.account
        else:
            raise WrongToken('Wrong token')
