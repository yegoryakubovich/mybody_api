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

from app.db.models import Training
from .base import BaseRepository
from app.db.models import AccountService


class TrainingRepository(BaseRepository):
    model = Training

    @staticmethod
    async def get_list_by_account_service(
            account_service: AccountService,
            date_: date = None,
    ) -> list[Training]:
        if date_:
            return Training.select().where(
                (Training.account_service == account_service) &
                (Training.date == date_) &
                (Training.is_deleted == False)
            ).execute()
        else:
            return Training.select().where(
                (Training.account_service == account_service) &
                (Training.is_deleted == False)
            ).execute()
