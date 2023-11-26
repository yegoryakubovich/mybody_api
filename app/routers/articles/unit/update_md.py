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


from typing import Optional

from pydantic import BaseModel, Field

from app.services import ArticleService
from app.utils import Router, Response


router = Router(
    prefix='/md/update',
)


class ArticleUpdateMdSchema(BaseModel):
    token: str = Field(min_length=32, max_length=64)
    language: Optional[str] = Field(max_length=32, default=None)
    md: str = Field(min_length=0, max_length=8192)


@router.post()
async def route(schema: ArticleUpdateMdSchema, article_id: int):
    result = await ArticleService().update_md(
        token=schema.token,
        article_id=article_id,
        language_id_str=schema.language,
        md=schema.md,
    )
    return Response(**result)
