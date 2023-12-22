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


from app.db.models import Article, Session
from app.repositories import ArticleRepository, ProductRepository
from app.services.text import TextService
from app.services.base import BaseService
from app.utils import ApiException, ProductTypes
from app.utils.crypto import create_id_str
from app.utils.decorators import session_required


class NoRequiredParameters(ApiException):
    pass


class InvalidProductType(ApiException):
    pass


class ProductService(BaseService):

    @session_required()
    async def create(
            self,
            session: Session,
            name: str,
            type_: str,
            article_id: int = None,
    ):
        await self.check_product_type(type_=type_)
        name_text_key = f'product_{await create_id_str()}'
        name_text = await TextService().create(
            session=session,
            key=name_text_key,
            value_default=name,
            return_model=True,
        )

        action_parameters = {
            'creator': f'session_{session.id}',
            'name_text_id': name_text.id,
            'type': type_,
        }

        if article_id:
            article = await ArticleRepository().get_by_id(id_=article_id)
            action_parameters.update(
                {
                    'article': article_id,
                }
            )
        else:
            article = None

        product = await ProductRepository().create(
            name_text=name_text,
            type_=type_,
            article=article,
        )

        await self.create_action(
            model=product,
            action='create',
            parameters=action_parameters,
        )

        return {'product_id': product.id}

    @session_required()
    async def update(
            self,
            session: Session,
            id_: int,
            type_: str = None,
            article_id: int = None,
    ):
        product = await ProductRepository().get_by_id(id_=id_)

        action_parameters = {
            'updater': f'session_{session.id}',
            'id': id_,
        }
        if not type_ and not article_id:
            raise NoRequiredParameters('One of the following parameters must be filled in: type_, article')
        if type_:
            await self.check_product_type(type_=type_)
            action_parameters.update(
                {
                    'type': type_,
                }
            )
        if article_id:
            article = await ArticleRepository().get_by_id(id_=article_id)
            action_parameters.update(
                {
                    'article': article_id,
                }
            )
        else:
            article = None

        await ProductRepository().update(product=product, type_=type_, article=article)

        await self.create_action(
            model=product,
            action='update',
            parameters=action_parameters,
        )

        return {}

    @session_required()
    async def delete(
            self,
            session: Session,
            id_: int,
    ):
        product = await ProductRepository().get_by_id(id_=id_)
        await ProductRepository().delete(model=product)
        await TextService().delete(
            session=session,
            key=product.name_text.key,
        )

        await self.create_action(
            model=product,
            action='delete',
            parameters={
                'deleter': f'session_{session.id}',
                'id': id_,
            },
        )

        return {}

    async def get_list_by_type(self, type_: str):
        await self.check_product_type(type_=type_)
        return {
            'products': [
                {
                    'id': product.id,
                    'name_text': product.name_text.key,
                } for product in await ProductRepository().get_list_by_type(type_=type_)
            ]
        }

    @staticmethod
    async def get(id_: int):
        product = await ProductRepository().get_by_id(id_=id_)
        return {
            'product': {
                'name_text': product.name_text.key,
                'type': product.type,
            }
        }

    @staticmethod
    async def get_list():
        return {
            'products': [
                {
                    'id': product.id,
                    'name_text': product.name_text.key,
                    'type': product.type,
                } for product in await ProductRepository().get_list()
            ]
        }

    @staticmethod
    async def check_product_type(type_: str):
        if type_ not in ProductTypes.all:
            raise InvalidProductType(f'Invalid product type. Available: {ProductTypes.all}')
