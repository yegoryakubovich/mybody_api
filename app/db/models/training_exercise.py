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


from peewee import BooleanField, IntegerField, PrimaryKeyField, ForeignKeyField

from .base import BaseModel
from .exercise import Exercise
from .training import Training


class TrainingExercise(BaseModel):
    id = PrimaryKeyField()
    training = ForeignKeyField(model=Training)
    exercise = ForeignKeyField(model=Exercise)
    priority = IntegerField()
    value = IntegerField()
    rest = IntegerField()
    is_deleted = BooleanField(default=False)

    class Meta:
        db_table = 'trainings_exercises'
