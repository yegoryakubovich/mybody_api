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


from app.db.models import Session
from app.repositories import LanguageRepository
from app.services.base import BaseService
from app.utils.decorators import session_required


class LanguageService(BaseService):
    @session_required()
    async def create(
            self,
            session: Session,
            id_str: str,
            name: str,
    ):
        language = await LanguageRepository().create(
            id_str=id_str,
            name=name,
        )

        await self.create_action(
            model=language,
            action='create',
            parameters={
                'creator': f'session_{session.id}',
                'id_str': language.id_str,
                'name': language.name,
            },
            with_client=True,
        )
        return {'id': language.id}

    @staticmethod
    async def get_list() -> dict:
        languages = {
            'languages': [
                {
                    'id': language.id,
                    'id_str': language.id_str,
                    'name': language.name,
                }
                for language in await LanguageRepository().get_list()
            ],
        }
        return languages

