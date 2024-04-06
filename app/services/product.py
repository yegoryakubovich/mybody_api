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


from app.db.models import Product, Session
from app.repositories import ArticleRepository, ProductRepository
from app.services.text import TextService
from app.services.base import BaseService
from app.utils import Units
from app.utils.crypto import create_id_str
from app.utils.decorators import session_required
from app.utils.exceptions import InvalidProductType, InvalidUnit, NoRequiredParameters


class ProductTypes:
    PROTEINS = 'proteins'
    FATS = 'fats'
    CARBOHYDRATES = 'carbohydrates'

    def all(self):
        return [self.PROTEINS, self.FATS, self.CARBOHYDRATES]


class ProductService(BaseService):

    @session_required(permissions=['products'])
    async def create_by_admin(
            self,
            session: Session,
            name: str,
            type_: str,
            unit: str,
            fats: float,
            proteins: float,
            carbohydrates: float,
            calories: int = None,
            article_id: int = None,
            is_main: bool = False,
    ):
        await self.check_product_type(type_=type_)
        await self.check_unit(unit=unit)
        name_text_key = f'product_{await create_id_str()}'
        name_text = await TextService().create_by_admin(
            session=session,
            key=name_text_key,
            value_default=name,
            return_model=True,
        )

        action_parameters = {
            'creator': f'session_{session.id}',
            'name_text_id': name_text.id,
            'type': type_,
            'unit': unit,
            'fats': fats,
            'proteins': proteins,
            'carbohydrates': carbohydrates,
            'is_main': is_main,
            'by_admin': True,
        }

        if article_id:
            article = await ArticleRepository().get_by_id(id_=article_id)
            action_parameters.update(
                {
                    'article_id': article_id,
                }
            )
        else:
            article = None

        if calories:
            action_parameters.update(
                {
                    'calories': calories,
                }
            )

        product = await ProductRepository().create(
            name_text=name_text,
            is_main=is_main,
            type=type_,
            unit=unit,
            fats=fats,
            proteins=proteins,
            carbohydrates=carbohydrates,
            calories=calories,
            article=article,
        )

        await self.create_action(
            model=product,
            action='create',
            parameters=action_parameters,
        )

        return {'id': product.id}

    @session_required(permissions=['products'])
    async def update_by_admin(
            self,
            session: Session,
            id_: int,
            type_: str = None,
            unit: str = None,
            fats: float = None,
            proteins: float = None,
            carbohydrates: float = None,
            calories: int = None,
            article_id: int = None,
            is_main: bool = False,
    ):
        product = await ProductRepository().get_by_id(id_=id_)

        action_parameters = {
            'updater': f'session_{session.id}',
            'by_admin': True,
        }
        if not type_ \
                and not unit \
                and not article_id \
                and not calories \
                and not fats \
                and not proteins \
                and not carbohydrates \
                and not is_main:
            raise NoRequiredParameters(
                kwargs={
                    'parameters': [
                        'type',
                        'unit',
                        'fats',
                        'proteins',
                        'carbohydrates',
                        'calories',
                        'article_id',
                        'is_main',
                    ]
                }
            )
        if type_:
            await self.check_product_type(type_=type_)
            action_parameters['type'] = type_
        if unit:
            await self.check_unit(unit=unit)
            action_parameters['unit'] = unit
        if fats:
            action_parameters['fats'] = fats
        if proteins:
            action_parameters['proteins'] = proteins
        if carbohydrates:
            action_parameters['carbohydrates'] = carbohydrates
        if calories:
            action_parameters['calories'] = calories
        if is_main:
            action_parameters['is_main'] = is_main
        if article_id:
            if article_id == -1:
                article = -1
                action_parameters.update(
                    {
                        'article_id': None,
                    }
                )
            else:
                article = await ArticleRepository().get_by_id(id_=article_id)
                action_parameters['article_id'] = article_id
        else:
            article = None

        await ProductRepository().update(
            model=product,
            type=type_,
            unit=unit,
            fats=fats,
            proteins=proteins,
            carbohydrates=carbohydrates,
            calories=calories,
            article=article,
            is_main=is_main,
        )

        await self.create_action(
            model=product,
            action='update',
            parameters=action_parameters,
        )

        return {}

    @session_required(permissions=['products'])
    async def delete_by_admin(
            self,
            session: Session,
            id_: int,
    ):
        product = await ProductRepository().get_by_id(id_=id_)
        await ProductRepository().delete(model=product)
        await TextService().delete_by_admin(
            session=session,
            key=product.name_text.key,
        )

        await self.create_action(
            model=product,
            action='delete',
            parameters={
                'deleter': f'session_{session.id}',
                'by_admin': True,
            },
        )

        return {}

    async def get_list_by_type(self, type_: str):
        await self.check_product_type(type_=type_)
        return {
            'products': [
                await self._generate_product_dict(product=product)
                for product in await ProductRepository().get_list_by_type(type_=type_)
            ]
        }

    async def get(self, id_: int):
        product: Product = await ProductRepository().get_by_id(id_=id_)
        return {
            'product': await self._generate_product_dict(product=product)
        }

    async def get_list(self):
        return {
            'products': [
                await self._generate_product_dict(product=product)
                for product in await ProductRepository().get_list()
            ]
        }

    @staticmethod
    async def check_product_type(type_: str):
        all_ = ProductTypes().all()
        if type_ not in all_:
            raise InvalidProductType(
                kwargs={
                    'all': all_,
                },
            )

    @staticmethod
    async def check_unit(unit: str):
        all_ = Units().all()
        if unit not in all_:
            raise InvalidUnit(
                kwargs={
                    'all': all_,
                },
            )

    @staticmethod
    async def _generate_product_dict(product: Product):
        return {
            'id': product.id,
            'name_text': product.name_text.key,
            'type': product.type,
            'is_main': product.is_main,
            'unit': product.unit,
            'fats': product.fats,
            'proteins': product.proteins,
            'carbohydrates': product.carbohydrates,
            'calories': product.calories if product.calories else None,
            'article_id': product.article.id if product.article else None,
        }
