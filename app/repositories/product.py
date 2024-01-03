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


from app.db.models import Article, Product, Text
from .base import BaseRepository


class ProductRepository(BaseRepository):
    model = Product

    @staticmethod
    async def get_list_by_type(type_: str) -> list[Product]:
        return Product.select().where(
            (Product.type == type_) &
            (Product.is_deleted == False)
        ).execute()

    @staticmethod
    async def update(product: Product, type_: str = None, unit: str = None, article: Article = None):
        if type_:
            product.type = type_
        if unit:
            product.unit = unit
        if article:
            product.article = article
        product.save()
