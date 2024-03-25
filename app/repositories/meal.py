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

from app.db.models import AccountService, Meal
from app.repositories.base import BaseRepository
from app.utils.exceptions import ModelAlreadyExist


class MealRepository(BaseRepository):
    model = Meal

    async def create(self, **kwargs):
        try:
            account_service = kwargs.get('account_service')
            date_ = kwargs.get('date')
            type_ = kwargs.get('type')
            Meal.get(
                (Meal.account_service == account_service) &
                (Meal.date == date_) &
                (Meal.type == type_) &
                (Meal.is_deleted == False)
            )
            raise ModelAlreadyExist(
                kwargs={
                    'model': 'Meal',
                    'id_type': 'account_service, date, type',
                    'id_value': [account_service.id, str(date_), type_],
                },
            )
        except DoesNotExist:
            return await super().create(**kwargs)

    @staticmethod
    async def get_by_parameters(
            account_service: AccountService,
            date_: date,
            type_: str,
    ):
        try:
            return Meal.get(
                (Meal.account_service == account_service) &
                (Meal.date == date_) &
                (Meal.type == type_) &
                (Meal.is_deleted == False)
            )
        except DoesNotExist:
            return False

    @staticmethod
    async def get_list_by_account_service_and_date(
            account_service: AccountService,
            date_: date = None,
    ) -> list[Meal]:
        if date_:
            return Meal.select().where(
                (Meal.account_service == account_service) &
                (Meal.date == date_) &
                (Meal.is_deleted == False)
            ).execute()
        else:
            return Meal.select().where(
                (Meal.account_service == account_service) &
                (Meal.is_deleted == False)
            ).execute()

    @staticmethod
    async def is_exist_by_parameters(
            account_service: AccountService,
            date_: date,
            type_: str,
    ) -> bool:
        try:
            Meal.get(
                (Meal.account_service == account_service) &
                (Meal.date == date_) &
                (Meal.type == type_) &
                (Meal.is_deleted == False)
            )
            return True
        except DoesNotExist:
            return False
