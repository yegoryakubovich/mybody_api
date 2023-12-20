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

from app.db.models import Training, AccountService
from .base import BaseRepository


class TrainingRepository(BaseRepository):
    model = Training

    @staticmethod
    async def create(
            account_service: AccountService,
            date_: date,
    ):
        return Training.create(
            account_service=account_service,
            date=date_,
        )

    @staticmethod
    async def update(
            training: Training,
            date_: date,
    ):
        training.date = date_
        training.save()

    @staticmethod
    async def delete(
            training: Training,
    ):
        training.is_deleted = True
        training.save()
