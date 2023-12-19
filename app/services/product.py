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
from app.repositories import ProductRepository
from app.services.text import TextService
from app.services.base import BaseService
from app.utils import ApiException, Nutrient
from app.utils.crypto import create_id_str
from app.utils.decorators import session_required


class InvalidNutrientType(ApiException):
    pass


class ProductService(BaseService):

    @session_required()
    async def create(
            self,
            session: Session,
            name: str,
            nutrient_type: str,
    ):
        await self.check_nutrient_type(nutrient_type=nutrient_type)
        name_text_key = f'product_{await create_id_str()}'
        name_text = await TextService().create(
            session=session,
            key=name_text_key,
            value_default=name,
            return_model=True,
        )

        product = await ProductRepository().create(
            name_text=name_text,
            nutrient_type=nutrient_type
        )

        await self.create_action(
            model=product,
            action='create',
            parameters={
                'creator': f'session_{session.id}',
                'name_text_id': name_text.id,
                'nutrient_type': nutrient_type,
            }
        )

        return {'product_id': product.id}

    @session_required()
    async def update(
            self,
            session: Session,
            id_: int,
            nutrient_type: str,
    ):
        await self.check_nutrient_type(nutrient_type=nutrient_type)
        product = await ProductRepository().get_by_id(id_=id_)

        await ProductRepository().update(product=product, nutrient_type=nutrient_type)

        await self.create_action(
            model=product,
            action='update',
            parameters={
                'updater': f'session_{session.id}',
                'id': id_,
                'nutrient_type': nutrient_type,
            },
        )

        return {}

    @session_required()
    async def delete(
            self,
            session: Session,
            id_: int,
    ):
        product = await ProductRepository().get_by_id(id_=id_)
        await ProductRepository().delete(product=product)

        await self.create_action(
            model=product,
            action='delete',
            parameters={
                'deleter': f'session_{session.id}',
                'id': id_,
            },
        )

        return {}

    async def get_list_by_nutrient_type(self, nutrient_type: str):
        await self.check_nutrient_type(nutrient_type=nutrient_type)
        return {
            'products': [
                {
                    'id': product.id,
                    'name_text': product.name_text.key,
                } for product in await ProductRepository().get_list_by_nutrient_type(nutrient_type=nutrient_type)
            ]
        }

    @staticmethod
    async def get(id_: int):
        product = await ProductRepository().get_by_id(id_=id_)
        return {
            'name_text': product.name_text.key,
            'nutrient_type': product.nutrient_type,
        }

    @staticmethod
    async def get_list():
        return {
            'products': [
                {
                    'id': product.id,
                    'name_text': product.name_text.key,
                    'nutrient_type': product.nutrient_type,
                } for product in await ProductRepository().get_list()
            ]
        }

    @staticmethod
    async def check_nutrient_type(nutrient_type: str):
        if nutrient_type not in Nutrient.all:
            raise InvalidNutrientType(f'Invalid nutrient type. Available: {Nutrient.all}')
