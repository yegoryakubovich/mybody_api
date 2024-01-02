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
from datetime import datetime

from .base import BaseRepository
from app.utils import ApiException
from ..db.models import Account, AccountService, Service


class AccountServiceDoesNotExist(ApiException):
    pass


class NoRequiredParameters(ApiException):
    pass


class AccountServiceStates:
    creation = 'CREATION'
    payment = 'PAYMENT'
    active = 'ACTIVE'
    expired = 'EXPIRED'


class AccountServiceRepository(BaseRepository):
    model = AccountService

    @staticmethod
    async def update(
            account_service: AccountService,
            answers: str = None,
            state: str = None,
            datetime_from: datetime = None,
            datetime_to: datetime = None,
    ):
        if not answers and not state and not datetime_from and not datetime_to:
            raise NoRequiredParameters('One of the following parameters must be filled in: answers, state, '
                                       'datetime_from, datetime_to')
        if answers:
            account_service.answers = answers
        if state:
            account_service.state = state
        if datetime_from:
            account_service.datetime_from = datetime_from
        if datetime_to:
            account_service.datetime_to = datetime_to
        account_service.save()
