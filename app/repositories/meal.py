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


from datetime import date

from app.db.models import Meal, AccountService
from app.repositories.base import BaseRepository


class MealRepository(BaseRepository):
    model = Meal

    @staticmethod
    async def create(
            account_service: AccountService,
            date_: date,
            type_: str,
    ):
        return Meal.create(
            account_service=account_service,
            date=date_,
            type=type_,
        )

    @staticmethod
    async def update(
            meal: Meal,
            date_: date = None,
            type_: str = None,
    ):
        if date_:
            meal.date = date_
        if type_:
            meal.type = type_
        meal.save()
