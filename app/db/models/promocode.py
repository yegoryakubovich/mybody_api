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


from peewee import BooleanField, PrimaryKeyField, CharField, IntegerField, DateField

from .base import BaseModel


class Promocode(BaseModel):
    id = PrimaryKeyField()
    id_str = CharField(max_length=16)
    usage_quantity = IntegerField()
    remaining_quantity = IntegerField()
    date_from = DateField()
    date_to = DateField(null=True)
    type = CharField(max_length=8)
    is_deleted = BooleanField(default=False)

    class Meta:
        db_table = 'promocodes'
