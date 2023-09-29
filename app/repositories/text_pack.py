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


from app.db.models import Language, TextPack
from app.repositories.base import BaseRepository


class TextPackRepository(BaseRepository):
    model = TextPack

    @staticmethod
    async def get_current(language: Language) -> TextPack:
        text_pack = TextPack.select().where(TextPack.language == language).order_by(TextPack.id.desc()).get()
        return text_pack
