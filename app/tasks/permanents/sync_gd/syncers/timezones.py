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


from gspread import Spreadsheet

from ..utils.google_sheets_api_client import google_sheets_api_client
from ..utils.mybody_api_client import mybody_api_client


async def sync_timezones(table: Spreadsheet):

    sheet = await google_sheets_api_client.get_sheet_by_table_and_name(table=table, name='timezones')
    timezones_table = await google_sheets_api_client.get_rows(sheet=sheet)
    timezones_ids_str_table = [timezone.get('id_str') for timezone in timezones_table]

    timezones = await mybody_api_client.client.timezones.get_list()
    timezones_ids_str = [timezone.id_str for timezone in timezones]

    match = list(set(timezones_ids_str) & set(timezones_ids_str_table))
    need_create = [id_str for id_str in timezones_ids_str_table if id_str not in match]
    need_delete = [id_str for id_str in timezones_ids_str if id_str not in match]

    for id_str in need_delete:
        await mybody_api_client.admin.timezones.delete(
            id_str=id_str,
        )

    for timezone_table in timezones_table:
        id_str = timezone_table.get('id_str')
        deviation = timezone_table.get('deviation')
        if timezone_table.get('id_str') in need_create:
            await mybody_api_client.admin.timezones.create(
                id_str=id_str,
                deviation=deviation,
            )
