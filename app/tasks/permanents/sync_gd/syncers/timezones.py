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


from addict import Dict
from gspread import Spreadsheet

from ..utils.google_sheets_api_client import google_sheets_api_client
from ..utils.mybody_api_client import mybody_api_client


async def sync_timezones(table: Spreadsheet):

    sheet = await google_sheets_api_client.get_sheet_by_table_and_name(table=table, name='timezones')
    timezones_table = await google_sheets_api_client.get_rows(sheet=sheet)
    timezones_keys_table = [timezone.get('key') for timezone in timezones_table]

    timezones = await mybody_api_client.client.timezones.get_list()
    timezones_keys = [timezone.key for timezone in timezones]

    match = list(set(timezones_keys) & set(timezones_keys_table))
    need_create = [key for key in timezones_keys_table if key not in match]
    need_delete = [key for key in timezones_keys if key not in match]

    for timezone_table in timezones_table:
