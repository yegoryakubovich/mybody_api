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


from peewee import CharField, DateTimeField, ForeignKeyField, PrimaryKeyField, BooleanField, TextField

from .account import Account
from .service import Service
from .base import BaseModel


class AccountService(BaseModel):
    id = PrimaryKeyField()
    account = ForeignKeyField(model=Account, backref='services')
    service = ForeignKeyField(model=Service, backref='accounts')
    questions = TextField(default=None, null=True)
    answers = TextField(default=None, null=True)
    state = CharField(max_length=64)
    datetime_from = DateTimeField(null=True, default=None)
    datetime_to = DateTimeField(null=True, default=None)
    is_deleted = BooleanField(default=False)

    class Meta:
        db_table = 'accounts_services'
