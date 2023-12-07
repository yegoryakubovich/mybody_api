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


from pydantic import BaseModel, Field

from app.services import TextTranslationService
from app.utils import Response, Router


router = Router(
    prefix='/update',
)


class TextTranslationUpdateSchema(BaseModel):
    token: str = Field(min_length=32, max_length=64)
    text_key: str = Field(min_length=2, max_length=128)
    language_id_str: str = Field(min_length=2, max_length=128)
    value: str = Field(min_length=1, max_length=1024)


@router.post()
async def route(schema: TextTranslationUpdateSchema):
    result = await TextTranslationService().update(
        token=schema.token,
        text_key=schema.text_key,
        language_id_str=schema.language_id_str,
        value=schema.value,
    )
    return Response(**result)
