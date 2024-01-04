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


from .base import BaseRepository
from ..db.models import MealReport, MealReportProduct


class MealReportProductRepository(BaseRepository):
    model = MealReportProduct

    @staticmethod
    async def get_list_by_meal_report(meal_report: MealReport) -> list[MealReportProduct]:
        return MealReportProduct().select().where(
            (MealReportProduct.meal_report == meal_report) &
            (MealReportProduct.is_deleted == False)
        ).execute()
