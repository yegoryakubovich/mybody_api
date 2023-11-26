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


from peewee import DoesNotExist

from app.db.models import Text, Language, TextTranslation
from app.repositories.base import BaseRepository
from app.utils import ApiException


class TextDoesNotExist(ApiException):
    pass


class TextExist(ApiException):
    pass


class TextRepository(BaseRepository):
    model = Text

    async def create(self, key: str, value_default: str) -> Text:
        try:
            await self.get_by_key(key=key)
            raise TextExist(f'Text with key "{key}" already exist')
        except TextDoesNotExist:
            return Text.create(
                key=key,
                value_default=value_default,
            )

    @staticmethod
    async def get_by_key(key: str) -> Text:
        try:
            return Text.get((Text.key == key) & (Text.is_deleted == False))
        except DoesNotExist:
            raise TextDoesNotExist(f'Text with key "{key}" does not exist')

    @staticmethod
    async def get_value(text: Text, language: Language = None) -> str:
        try:
            translation = TextTranslation.get(
                (TextTranslation.text == text) &
                (TextTranslation.language == language) &
                (TextTranslation.is_deleted == False)
            )
            value = translation.value
        except DoesNotExist:
            value = text.value_default
        return value
