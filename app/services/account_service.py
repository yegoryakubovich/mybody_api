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


from json import JSONDecodeError, loads

from app.db.models import Account, AccountService, Service, Session
from app.repositories import AccountRepository, AccountServiceRepository, ServiceRepository, AccountServiceStates
from app.services.base import BaseService
from app.utils import ApiException
from app.utils.decorators import session_required


class InvalidAnswerList(ApiException):
    pass


class AccountServiceService(BaseService):

    async def check_answers(self, questions: str, answers: str):
        if not await self._is_valid_answers(questions=questions, answers=answers):
            raise InvalidAnswerList('Invalid answer list')

    async def _create(
            self,
            session: Session,
            account: Account,
            service: Service,
            answers: str,
    ) -> AccountService:
        state = AccountServiceStates.creation
        await self.check_answers(questions=service.questions, answers=answers)
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
                'account_id': account.id,
                'service': service.id_str,
                'questions': service.questions,
                'answers': answers,
                'state': state,
            },
        )
        return account_service

    @session_required()
    async def create(
            self,
            session: Session,
            account_id: int,
            service_id_str: str,
            answers: str,
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
            answers: str,
    ):
        account = session.account
        service: Service = await ServiceRepository().get_by_id_str(id_str=service_id_str)
        account_service = await self._create(session=session, account=account, service=service, answers=answers)
        return {'id': account_service.id}

    @session_required()
    async def update(
            self,
            session: Session,
            id_: int,
            answers: str = None,
            state: str = None,
    ):
        account_service: AccountService = await AccountServiceRepository().get_by_id(id_=id_)
        if answers:
            await self.check_answers(questions=account_service.questions, answers=answers)
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

        await AccountServiceRepository().delete(model=account_service)

        await self.create_action(
            model=account_service,
            action='delete',
            parameters={
                'deleter': f'session_{session.id}',
                'id': id_,
            },
        )
        return {}

    @session_required(return_model=False)
    async def get(
            self,
            id_: int,
    ):
        account_service: AccountService = await AccountServiceRepository().get_by_id(id_=id_)
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

    @session_required(return_model=False)
    async def get_list(
            self,
    ):
        response = {
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
        return response

    @staticmethod
    async def _is_valid_answers(questions: str, answers: str):
        try:
            questions = loads(questions)
            answers = loads(answers)
            if len(answers) != len(questions):
                return False
            for i in range(len(answers)):
                if questions[i]['type'] == 'dropdown':
                    if answers[i] not in questions[i]['values']:
                        return False
                if questions[i]['type'] == 'str' and type(answers[i]) != str:
                    return False
                if questions[i]['type'] == 'int' and type(answers[i]) != int:
                    return False
            return True
        except JSONDecodeError:
            return False
        except TypeError:
            return False
        except KeyError:
            return False
