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

from app.db.models import DayTraining, Day
from .base import BaseRepository
from ..utils.exceptions import ModelAlreadyExist


class DayTrainingRepository(BaseRepository):
    model = DayTraining

    @staticmethod
    async def get_by_day(day: Day) -> DayTraining | bool:
        try:
            return DayTraining.get(
                (DayTraining.day == day) &
                (DayTraining.is_deleted == False)
            )
        except DoesNotExist:
            return False

    async def create(self, **kwargs):
        try:
            day = kwargs.get('day')
            training = kwargs.get('training')
            DayTraining.get(
                (DayTraining.day == day) &
                (DayTraining.training == training) &
                (DayTraining.is_deleted == False)
            )
            raise ModelAlreadyExist(
                kwargs={
                    'model': 'DayMeal',
                    'id_type': 'day, training',
                    'id_value': [day.id, training.id],
                },
            )
        except DoesNotExist:
            return await super().create(**kwargs)

