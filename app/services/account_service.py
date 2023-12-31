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


from datetime import datetime
from json import JSONDecodeError, loads

from app.db.models import Account, AccountService, Service, Session
from app.repositories import AccountRepository, AccountServiceRepository, ServiceRepository, AccountServiceStates
from app.services.base import BaseService
from app.utils import ApiException
from app.utils.decorators.session_required import session_required


class InvalidAnswerList(ApiException):
    pass


class NotEnoughPermissions(ApiException):
    pass


class AccountServiceService(BaseService):

    async def check_answers(self, questions: str, answers: str):
        if not await self._is_valid_answers(questions_sections=questions, answers=answers):
            raise InvalidAnswerList('Invalid answer list')

    async def _create(
            self,
            session: Session,
            account: Account,
            service: Service,
            answers: str = None,
    ) -> AccountService:
        state = AccountServiceStates.creation
        action_parameters = {
            'creator': f'session_{session.id}',
            'account_id': account.id,
            'service': service.id_str,
            'state': state,
            'by_admin': True,
        }
        if service.questions:
            action_parameters.update(
                {
                    'questions': service.questions,
                    'answers': answers,
                }
            )
            await self.check_answers(questions=service.questions, answers=answers)
        else:
            answers = None
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
            parameters=action_parameters,
        )
        return account_service

    @session_required(permissions=['accounts'])
    async def create_by_admin(
            self,
            session: Session,
            account_id: int,
            service_id_str: str,
            answers: str = None,
    ):
        account: Account = await AccountRepository().get_by_id(id_=account_id)
        service: Service = await ServiceRepository().get_by_id_str(id_str=service_id_str)
        account_service = await self._create(session=session, account=account, service=service, answers=answers)
        return {'id': account_service.id}

    @session_required()
    async def create_additional(
            self,
            session: Session,
            service_id_str: str,
            answers: str = None,
    ):
        account = session.account
        service: Service = await ServiceRepository().get_by_id_str(id_str=service_id_str)
        account_service = await self._create(session=session, account=account, service=service, answers=answers)
        return {'id': account_service.id}

    @session_required(permissions=['accounts'])
    async def update_by_admin(
            self,
            session: Session,
            id_: int,
            answers: str = None,
            state: str = None,
            datetime_from: str = None,
            datetime_to: str = None,
    ):
        account_service: AccountService = await AccountServiceRepository().get_by_id(id_=id_)
        if answers:
            await self.check_answers(questions=account_service.questions, answers=answers)
        if datetime_from:
            datetime_from = datetime.strptime(datetime_from, '')  # FIXME format
        if datetime_to:
            datetime_to = datetime.strptime(datetime_to, '')  # FIXME format
        await AccountServiceRepository().update(
            model=account_service,
            answers=answers,
            state=state,
            datetime_from=datetime_from,
            datetime_to=datetime_to,
        )

        action_parameters = {
            'updater': f'session_{session.id}',
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

    @session_required(permissions=['accounts'])
    async def delete_by_admin(
            self,
            session: Session,
            id_: int,
    ):
        account_service: AccountService = await AccountServiceRepository().get_by_id(id_=id_)

        await AccountServiceRepository().delete(model=account_service)

        await self.create_action(
            model=account_service,
            action='delete',
            parameters={
                'deleter': f'session_{session.id}',
            },
        )
        return {}

    @staticmethod
    async def _get(
            session: Session,
            id_: int,
            by_admin: bool = False,
    ):
        account_service: AccountService = await AccountServiceRepository().get_by_id(id_=id_)
        if account_service.account != session.account and not by_admin:
            raise NotEnoughPermissions('Not enough permissions to execute')
        return {
            'account_service': {
                'id': account_service.id,
                'account': account_service.account.id,
                'service': account_service.service.id,
                'questions': account_service.questions,
                'answers': account_service.answers,
                'state': account_service.state,
            }
        }

    @session_required()
    async def get(
            self,
            session: Session,
            id_: int,
    ):
        return await self._get(
            session=session,
            id_=id_,
        )

    @session_required(permissions=['accounts'])
    async def get_by_admin(
            self,
            session: Session,
            id_: int,
    ):
        return await self._get(
            session=session,
            id_=id_,
            by_admin=True,
        )

    @session_required(permissions=['accounts'], return_model=False)
    async def get_list_by_admin(self):
        return {
            'accounts_services': [
                {
                    'id': account_service.id,
                    'account': account_service.account.id,
                    'service': account_service.service.id,
                    'questions': account_service.questions,
                    'answers': account_service.answers,
                    'state': account_service.state,
                } for account_service in await AccountServiceRepository().get_list()
            ]
        }

    @session_required()
    async def get_list(
            self,
            session: Session,
    ):
        return {
            'account_services': [
                {
                    'id': account_service.id,
                    'account': account_service.account.id,
                    'service': account_service.service.id,
                    'questions': account_service.questions,
                    'answers': account_service.answers,
                    'state': account_service.state,
                } for account_service in await AccountServiceRepository().get_list_by_account(account=session.account)
            ]
        }

    @staticmethod
    async def _is_valid_answers(questions_sections: str, answers: str):
        try:
            questions_sections = loads(questions_sections)
            questions_count = []
            for section in questions_sections:
                questions_count.append(len(section['questions']))
            answers: list = loads(answers)
            if len(answers) != sum(questions_count):
                return False
            for i in range(len(questions_count)):
                for j in range(questions_count[i]):
                    if questions_sections[i]['questions'][j]['type'] == 'dropdown':
                        if answers[0] not in questions_sections[i]['questions'][j]['values']:
                            return False
                    if questions_sections[i]['questions'][j]['type'] == 'str' and type(answers[0]) != str:
                        return False
                    if questions_sections[i]['questions'][j]['type'] == 'int' and type(answers[0]) != int:
                        return False
                    answers.pop(0)
            return True
        except JSONDecodeError:
            return False
        except TypeError:
            return False
        except KeyError:
            return False
