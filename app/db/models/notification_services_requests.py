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


from peewee import PrimaryKeyField, CharField, ForeignKeyField, BooleanField, DateTimeField

from .account import Account
from .base import BaseModel


class NotificationServiceRequest(BaseModel):
    id = PrimaryKeyField()
    account = ForeignKeyField(model=Account)
    name = CharField(max_length=32)
    value = CharField(max_length=256, null=True, default=None)
    verification_salt = CharField(max_length=32)
    verification_hash = CharField(max_length=32)
    verification_expired_datetime = DateTimeField()
    verification_can_repeat_datetime = DateTimeField()
    state = CharField(max_length=16)
    is_deleted = BooleanField(default=False)

    class Meta:
        db_table = 'notification_services_requests'
