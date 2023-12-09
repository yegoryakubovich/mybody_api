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


from peewee import CharField, ForeignKeyField, PrimaryKeyField

from app.db.models import Form, ServiceAccount
from app.db.models.base import BaseModel


class AccountForm(BaseModel):
    id = PrimaryKeyField()
    service_account = ForeignKeyField(model=ServiceAccount)
    fields = CharField(default='[]')
    form = ForeignKeyField(model=Form)

    class Meta:
        db_table = 'accounts_forms'
