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


from .base import BaseRepository
from ..db.models import Exercise, Training, TrainingExercise


class TrainingExerciseRepository(BaseRepository):
    model = TrainingExercise

    @staticmethod
    async def create(
            training: Training,
            exercise: Exercise,
            priority: int,
            value: int,
            rest: int,
    ):
        return TrainingExercise.create(
            training=training,
            exercise=exercise,
            priority=priority,
            value=value,
            rest=rest,
        )

    @staticmethod
    async def update(
            training_exercise: TrainingExercise,
            exercise: Exercise = None,
            priority: int = None,
            value: int = None,
            rest: int = None,
    ):
        if exercise:
            training_exercise.exercise = exercise
        if priority:
            training_exercise.priority = priority
        if value:
            training_exercise.value = value
        if rest:
            training_exercise.rest = rest
        training_exercise.save()

    @staticmethod
    async def get_list_by_training(training: Training) -> list[TrainingExercise]:
        return TrainingExercise().select().where(
            (TrainingExercise.training == training) &
            (TrainingExercise.is_deleted == False)
        ).execute()
