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


from app.db.models import Account, AccountService, Service, Session
from app.repositories import AccountRepository, AccountServiceRepository, ServiceRepository
from app.services.base import BaseService
from app.utils.decorators import session_required


class AccountServiceService(BaseService):
    @session_required()
    async def create(
            self,
            session: Session,
            account_username: str,
            service_id_str: str,
            answers: str,
            state: str,
    ):
        account: Account = await AccountRepository().get_by_username(username=account_username)
        service: Service = await ServiceRepository().get_by_id_str(id_str=service_id_str)
        account_service = await AccountServiceRepository().create(
            account=account,
            service=service,
            questions=service.questions,
            answers=answers,
            state=state,
        )

        await self.create_action(
            model=account_service,
            action='create',
            parameters={
                'creator': f'session_{session.id}',
                'account': account.username,
                'service': service.id_str,
                'questions': service.questions,
                'answers': answers,
                'state': state,
            },
        )
        return {}

    @session_required()
    async def update(
            self,
            session: Session,
            id_: int,
            answers: str = None,
            state: str = None,
    ):
        account_service: AccountService = await AccountServiceRepository().get_by_id(id_=id_)

        await AccountServiceRepository().update(
            account_service=account_service,
            answers=answers,
            state=state,
        )

        action_parameters = {
            'updater': f'session_{session.id}',
            'id': id_,
        }
        if answers:
            action_parameters.update(
                {
                    'answers': answers,
                }
            )
        if state:
            action_parameters.update(
                {
                    'state': state,
                }
            )

        await self.create_action(
            model=account_service,
            action='update',
            parameters=action_parameters,
        )
        return {}

    @session_required()
    async def delete(
            self,
            session: Session,
            id_: int,
    ):
        account_service: AccountService = await AccountServiceRepository().get_by_id(id_=id_)

        await AccountServiceRepository().delete(account_service=account_service)

        await self.create_action(
            model=account_service,
            action='delete',
            parameters={
                'deleter': f'session_{session.id}',
                'id': id_,
            },
        )
        return {}
