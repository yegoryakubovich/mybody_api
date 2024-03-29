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


from peewee import DoesNotExist

from app.db.models import ArticleTranslation, Article, Language
from .base import BaseRepository, ModelDoesNotExist


class ArticleTranslationRepository(BaseRepository):
    model = ArticleTranslation

    @staticmethod
    async def get(
            article: Article,
            language: Language,
    ) -> ArticleTranslation:
        try:
            return ArticleTranslation.get(
                (ArticleTranslation.article == article) &
                (ArticleTranslation.language == language) &
                (ArticleTranslation.is_deleted == False)
            )
        except DoesNotExist:
            raise ModelDoesNotExist(
                kwargs={
                    'model': 'ArticleTranslation',
                    'id_type': 'article, language',
                    'id_value': [article.id, language.id_str],
                },
            )

    @staticmethod
    async def get_list_by_article(article: Article) -> list[ArticleTranslation]:
        return ArticleTranslation.select().where(
            (ArticleTranslation.article == article) &
            (ArticleTranslation.is_deleted == False)
        ).execute()

    @staticmethod
    async def is_exist_by_article_and_language(
            article: Article,
            language: Language,
    ) -> bool:
        try:
            ArticleTranslation.get(
                (ArticleTranslation.article == article) &
                (ArticleTranslation.language == language) &
                (ArticleTranslation.is_deleted == False)
            )
            return True
        except DoesNotExist:
            return False
