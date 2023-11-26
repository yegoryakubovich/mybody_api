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


class TextTranslationDoesNotExist(ApiException):
    pass


class TextTranslationExist(ApiException):
    pass


class TextTranslationRepository(BaseRepository):
    model = TextTranslation

    @staticmethod
    async def get(text: Text, language: Language):
        try:
            return TextTranslation.get(
                (TextTranslation.text == text) &
                (TextTranslation.language == language) &
                (TextTranslation.is_deleted == False)
            )
        except DoesNotExist:
            raise TextTranslationDoesNotExist(f'Text translation with language "{language.id_str}" does not exist')

    async def create(self, text: Text, language: Language, value: str) -> TextTranslation:
        try:
            await self.get(text=text, language=language)
            raise TextTranslationExist(f'Text translation with language "{language.id_str}" already exist')
        except TextTranslationDoesNotExist:
            return TextTranslation.create(
                text=text,
                language=language,
                value=value,
            )
