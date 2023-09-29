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


from peewee import PrimaryKeyField, ForeignKeyField, CharField, BooleanField

from .parameter_account import ParameterAccount
from .account import Account
from .base import BaseModel


class AccountParameter(BaseModel):
    id = PrimaryKeyField()
    account = ForeignKeyField(model=Account, backref='parameters')
    parameter = ForeignKeyField(model=ParameterAccount)
    value = CharField(max_length=512)
    is_deleted = BooleanField(default=False)

    class Meta:
        db_table = 'accounts_parameters'
