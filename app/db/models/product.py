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


from peewee import BooleanField, PrimaryKeyField, CharField, ForeignKeyField, IntegerField, FloatField

from .article import Article
from .text import Text
from .base import BaseModel


class Product(BaseModel):
    id = PrimaryKeyField()
    name_text = ForeignKeyField(model=Text)
    type = CharField(max_length=16)
    is_main = BooleanField()
    unit = CharField(max_length=4)
    fats = FloatField()
    proteins = FloatField()
    carbohydrates = FloatField()
    calories = IntegerField(null=True)
    article = ForeignKeyField(null=True, model=Article)
    is_deleted = BooleanField(default=False)

    class Meta:
        db_table = 'products'
