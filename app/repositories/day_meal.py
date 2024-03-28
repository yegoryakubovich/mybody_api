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

from peewee import DoesNotExist

from app.db.models import DayMeal, Day, Meal
from .base import BaseRepository
from ..utils.exceptions import ModelAlreadyExist


class DayMealRepository(BaseRepository):
    model = DayMeal

    @staticmethod
    async def get_list_by_day(day: Day) -> list[DayMeal]:
        return DayMeal.select().where(
            (DayMeal.day == day) &
            (DayMeal.is_deleted == False)
        ).execute()

    @staticmethod
    async def get_by_day_and_meal(
            day: Day,
            meal: Meal,
    ):
        try:
            return DayMeal.get(
                (DayMeal.day == day) &
                (DayMeal.meal == meal) &
                (DayMeal.is_deleted == False)
            )
        except DoesNotExist:
            return False

    async def create(self, **kwargs):
        try:
            day = kwargs.get('day')
            meal = kwargs.get('meal')
            DayMeal.get(
                (DayMeal.day == day) &
                (DayMeal.meal == meal) &
                (DayMeal.is_deleted == False)
            )
            raise ModelAlreadyExist(
                kwargs={
                    'model': 'DayMeal',
                    'id_type': 'day, meal',
                    'id_value': [day.id, meal.id],
                },
            )
        except DoesNotExist:
            return await super().create(**kwargs)

