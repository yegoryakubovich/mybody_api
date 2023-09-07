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


from peewee import PrimaryKeyField, CharField, ForeignKeyField, BooleanField

from app.db.models.base import BaseModel
from app.db.models.country import Country
from app.db.models.currency import Currency
from app.db.models.language import Language
from app.db.models.timezone import Timezone


class Account(BaseModel):
    id = PrimaryKeyField()
    username = CharField(max_length=32)
    password = CharField(max_length=128)
    password_salt = CharField(max_length=128)
    firstname = CharField(max_length=32)
    lastname = CharField(max_length=32)
    surname = CharField(max_length=32, null=True)
    country = ForeignKeyField(model=Country)
    language = ForeignKeyField(model=Language)
    timezone = ForeignKeyField(model=Timezone)
    currency = ForeignKeyField(model=Currency)
    is_deleted = BooleanField(default=False)

    class Meta:
        db_table = 'accounts'
