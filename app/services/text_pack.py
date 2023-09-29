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


from app.db.models import Text, Language, TextPack
from app.repositories import TextRepository
from app.services.base import BaseService


class TextPackService(BaseService):
    model = TextPack

    async def create(self, language: Language) -> TextPack:
        pack = {}
        for text in Text.select():
            key = text
            value = TextRepository.get_value(text=text, language=language)
            pack[key] = value

        text_pack = TextPack.create(language=language, pack=pack)
        await self.create_action(
            model=text_pack,
            action='create',
            parameters={
                'creator': 'system',
            },
        )
        return text_pack

    async def create_all(self):
        for language in Language.select():
            await self.create(language=language)

    @staticmethod
    async def get(language: Language) -> TextPack:
        text_pack = TextPack.select().where(TextPack.language == language).order_by(TextPack.id.desc()).get()
        return text_pack
