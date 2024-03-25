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

from .base import BaseRepository
from ..db.models import Training, TrainingReport


class TrainingReportRepository(BaseRepository):
    model = TrainingReport

    @staticmethod
    async def is_exist_by_training(training: Training):
        try:
            tr = TrainingReport.get((TrainingReport.training == training) & (TrainingReport.is_deleted == False))
            return True
        except DoesNotExist:
            return False

    @staticmethod
    async def get_by_training(training: Training):
        try:
            return TrainingReport.get((TrainingReport.training == training) & (TrainingReport.is_deleted == False))
        except DoesNotExist:
            return False
