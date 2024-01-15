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


from app.db.models import Session, Article
from app.repositories import ArticleRepository, LanguageRepository, ArticleTranslationRepository
from app.repositories.text_translation import TextTranslationRepository
from app.services.base import BaseService
from app.utils import ApiException
from app.utils.decorators import session_required
from config import PATH_ARTICLES


class ArticleTranslationExist(ApiException):
    pass


class ArticleTranslationService(BaseService):
    @session_required(permissions=['articles'])
    async def create_by_admin(
            self,
            session: Session,
            article_id: int,
            language_id_str: str,
            name: str = None,
    ) -> dict:
        article = await ArticleRepository().get_by_id(id_=article_id)
        language = await LanguageRepository().get_by_id_str(id_str=language_id_str)

        if await ArticleTranslationRepository().is_exist_by_article_and_language(
            article=article,
            language=language,
        ):
            raise ArticleTranslationExist(
                f'The article (id {article.id}) already has a translation into {language.id_str} language'
            )

        # Create article translation
        article_translation = await ArticleTranslationRepository().create(
            article=article,
            language=language,
        )
        name_text_translation = await TextTranslationRepository().create(
            text=article.name_text,
            language=language,
            value=name or article.name_text.value_default,
        )

        # Create action
        await self.create_action(
            model=article_translation,
            action='create',
            parameters={
                'creator': f'session_{session.id}',
                'name_text_translation_id': name_text_translation.id,
                'name': name,
                'by_admin': True,
            },
        )

        # Create md file
        with open(f'{PATH_ARTICLES}/{article.id}_{language.id_str}.md', encoding='utf-8', mode='w') as md_file:
            md_file.write('')

        return {'id': article_translation.id}

    @session_required(permissions=['articles'])
    async def delete_by_admin(
            self,
            session: Session,
            article_id: int,
            language_id_str: str,
    ) -> dict:
        language = await LanguageRepository().get_by_id_str(id_str=language_id_str)
        article: Article = await ArticleRepository().get_by_id(id_=article_id)
        article_translation = await ArticleTranslationRepository().get(
            article=article,
            language=language,
        )
        text_translation = await TextTranslationRepository().get(text=article.name_text, language=language)
        await ArticleTranslationRepository.delete(model=article_translation)
        await TextTranslationRepository().delete(model=text_translation)

        # Create action
        await self.create_action(
            model=article_translation,
            action='delete',
            parameters={
                'deleter': f'session_{session.id}',
                'by_admin': True,
            },
        )

        return {}
