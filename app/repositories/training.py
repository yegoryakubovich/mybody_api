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


from datetime import date

from peewee import DoesNotExist

from app.db.models import Training
from .base import BaseRepository
from app.db.models import AccountService
from ..utils.exceptions import ModelDoesNotExist


class TrainingRepository(BaseRepository):
    model = Training

    @staticmethod
    async def get_list_by_account_service(
            account_service: AccountService,
    ) -> list[Training]:
        return Training.select().where(
            (Training.account_service == account_service) &
            (Training.is_deleted == False)
        ).execute()

    @staticmethod
    async def is_exist_by_date_and_account_service(
            account_service: AccountService,
            date_: date,
    ):
        try:
            Training.select().where(
                (Training.account_service == account_service) &
                (Training.date == date_) &
                (Training.is_deleted == False)
            ).execute()
            return True
        except DoesNotExist:
            return False

    @staticmethod
    async def get_by_date_and_account_service(
            account_service: AccountService,
            date_: date,
    ):

        try:
            return Training.get(
                (Training.account_service == account_service) &
                (Training.date == date_) &
                (Training.is_deleted == False)
            )
        except DoesNotExist:
            raise ModelDoesNotExist(
                kwargs={
                    'model': 'Training',
                    'id_type': ['date', 'account_service'],
                    'id_value': [str(date_), account_service.id],
                },
            )
