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


PREFIXES = [
    'permission_',
    'role_',
    'service_',
    'product_',
    'exercise_',
    'article_',
    'timezone_',
]
DEFAULT_LANGUAGE = 'eng'


async def sync_texts(table: Spreadsheet):
    languages = await mybody_api_client.client.languages.get_list()

    sheet_texts = await google_sheets_api_client.get_sheet_by_table_and_name(table=table, name='texts')
    rows_texts = await google_sheets_api_client.get_rows(sheet=sheet_texts)

    sheet_error = await google_sheets_api_client.get_sheet_by_table_and_name(table=table, name='errors')
    rows_error = await google_sheets_api_client.get_rows(sheet=sheet_error)

    texts_table = rows_texts + [
        Dict(
            key=f'error_{error.code}',
            **{
                key: value for key, value in error.items() if key not in ['code', 'class']
            },
        ) for error in rows_error
    ]

    sheet_keys = [row.get('key') for row in texts_table]

    texts = await mybody_api_client.admin.texts.get_list()
    texts_keys = [text.key for text in texts]
    texts_api = Dict(
        **{
            text.key: dict(
                default_value=text.value_default,
                translations={
                    translation.language: translation.value for translation in text.translations
                },
            ) for text in texts
        }
    )
    match = list(set(sheet_keys) & set(texts_keys))

    need_create = [key for key in sheet_keys if key not in match]
    need_delete = [key for key in texts_keys if key not in match and not key.startswith(tuple(PREFIXES))]

    for text_table in texts_table:
        key = text_table.key
        text_api = texts_api.get(key)

        if key in need_create:
            continue
        if key in need_delete:
            continue

        current_value_default = text_api.get('default_value')
        new_value_default = text_table.get(DEFAULT_LANGUAGE)

        #print(text_api)
        # print(text_table)

        if current_value_default != new_value_default:
            print(key, new_value_default)
            await mybody_api_client.admin.texts.update(key=key, value_default=new_value_default)




    # languages = await mybody_api_client.client.languages.get_list()
    # print(languages)