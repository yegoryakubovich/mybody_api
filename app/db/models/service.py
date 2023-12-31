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


from json import loads

from peewee import BooleanField, CharField, ForeignKeyField, PrimaryKeyField

from .text import Text
from .base import BaseModel


class Service(BaseModel):
    id = PrimaryKeyField()
    id_str = CharField(max_length=64)
    name_text = ForeignKeyField(model=Text)
    questions = CharField(null=True, default=None, max_length=8192)
    is_deleted = BooleanField(default=False)

    async def get_questions(self):
        return loads(str(self.questions))

    class Meta:
        db_table = 'services'
