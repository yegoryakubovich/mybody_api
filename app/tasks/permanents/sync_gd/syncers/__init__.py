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


from app.tasks.permanents.sync_gd.syncers.texts import sync_texts
from config import settings
from ..utils.google_sheets_api_client import google_sheets_api_client


async def sync():
    table = await google_sheets_api_client.get_table_by_name(name=settings.sync_db_table_name)
    await sync_texts(table=table)