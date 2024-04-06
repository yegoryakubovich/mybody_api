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
from app.repositories import ArticleRepository, LanguageRepository, ArticleTranslationRepository, \
    TextRepository
from app.services import AccountRoleCheckPermissionService
from app.services.text import TextService
from app.services.base import BaseService
from app.utils.exceptions import ArticleSessionRequired, ModelDoesNotExist, NoRequiredParameters
from app.utils.crypto import create_id_str
from app.utils.decorators import session_required
from config import settings


class ArticleService(BaseService):
    @session_required(permissions=['articles'])
    async def create_by_admin(
            self,
            session: Session,
            name: str,
    ) -> dict:
        # Create text
        name_text_key = f'article_{await create_id_str()}'
        name_text = await TextService().create_by_admin(
            session=session,
            key=name_text_key,
            value_default=name,
            return_model=True,
        )

        # Create article
        article = await ArticleRepository().create(
            name_text=name_text,
        )

        # Create action
        await self.create_action(
            model=article,
            action='create',
            parameters={
                'creator': f'session_{session.id}',
                'name_text_id': name_text.id,
                'by_admin': True,
            },
        )

        # Create md file
        with open(f'{settings.path_articles}/{article.id}.md', encoding='utf-8', mode='w') as md_file:
            md_file.write('')

        return {'id': article.id}

    @session_required(permissions=['articles'])
    async def update_by_admin(
            self,
            session: Session,
            id_: int,
            is_hide: bool = False,
            can_guest: bool = False,
    ) -> dict:
        article: Article = await ArticleRepository().get_by_id(id_=id_)

        if not is_hide and not can_guest:
            raise NoRequiredParameters(
                kwargs={
                    'parameters': ['is_hide', 'can_guest']
                }
            )

        await ArticleRepository().update(
            model=article,
            is_hide=is_hide,
            can_guest=can_guest,
        )

        # Create action
        await self.create_action(
            model=article,
            action='update',
            parameters={
                'updater': f'session_{session.id}',
                'is_hide': is_hide,
                'can_guest': can_guest,
                'by_admin': True,
            },
        )

        return {}

    @session_required(permissions=['articles'])
    async def delete_by_admin(
            self,
            session: Session,
            id_: int,
    ) -> dict:
        article: Article = await ArticleRepository().get_by_id(id_=id_)
        await ArticleRepository.delete(model=article)

        # Create action
        await self.create_action(
            model=article,
            action='delete',
            parameters={
                'deleter': f'session_{session.id}',
                'by_admin': True,
            },
        )

        return {}

    @session_required(permissions=['articles'])
    async def update_md_by_admin(
            self,
            session: Session,
            id_: int,
            language_id_str: str,
            md: str,
            name: str = None,
    ) -> dict:
        article: Article = await ArticleRepository().get_by_id(id_=id_)
        language = await LanguageRepository().get_by_id_str(id_str=language_id_str) if language_id_str else None
        filename = f'{article.id}_{language.id_str}' if language else f'{article.id}'

        if language:
            await ArticleTranslationRepository.get(article=article, language=language)

        if name:
            await TextService().update_by_admin(
                session=session,
                key=article.name_text.key,
                value_default=name,
            )

        # Create action
        await self.create_action(
            model=article,
            action='update_md',
            parameters={
                'updater': f'session_{session.id}',
                'language': language.id_str if language else None,
                'by_admin': True,
            },
        )

        with open(f'{settings.path_articles}/{filename}.md', encoding='utf-8', mode='w') as md_file:
            md_file.truncate(0)
            md_file.write(md)

        return {}

    @session_required(return_model=False)
    async def get_list(self):
        articles_list = []

        articles = await ArticleRepository().get_list()
        for article in articles:
            article: Article
            articles_list.append(
                await self._generate_article_dict(article=article),
            )
        return {
            'articles': articles_list,
        }

    @session_required(return_model=False)
    async def get(self, id_):
        article = await ArticleRepository().get_by_id(id_=id_)
        return {
            'article': await self._generate_article_dict(article=article),
        }

    @session_required(can_guest=True)
    async def get_additional(
            self,
            session: Session,
            id_: int,
            language_id_str: str = None,
    ) -> dict:
        article: Article = await ArticleRepository().get_by_id(id_=id_)

        name_text = article.name_text
        name = name_text.value_default

        language = await LanguageRepository().get_by_id_str(id_str=language_id_str) if language_id_str else None
        language_id_str = None

        filename = f'{article.id}'

        # Checks associated with a hidden article
        if article.is_hide:
            if not session:
                raise ArticleSessionRequired()
            await AccountRoleCheckPermissionService().check_permission(account=session.account, id_str='articles')

        # Can guest
        if not article.can_guest and not session:
            raise ArticleSessionRequired()

        if language:
            try:
                await ArticleTranslationRepository.get(article=article, language=language)
                name = await TextRepository().get_value(text=name_text, language=language)
                language_id_str = language.id_str
                filename = f'{article.id}_{language_id_str}'
            except ModelDoesNotExist:
                pass

        with open(f'{settings.path_articles}/{filename}.md', encoding='utf-8', mode='r') as md_file:
            md = md_file.read()
        return {
            'article': {
                'can_guest': article.can_guest,
                'language': language_id_str,
                'name': name,
                'md': md,
            }
        }

    @staticmethod
    async def _generate_article_dict(article: Article):
        translations = await ArticleTranslationRepository().get_list_by_article(article=article)
        return {
            'id': article.id,
            'name_text': article.name_text.key,
            'can_guest': article.can_guest,
            'is_hide': article.is_hide,
            'translations': [
                {
                    'language': translation.language.id_str,
                }
                for translation in translations
            ],
        }
