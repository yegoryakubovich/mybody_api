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


from enum import Enum

from peewee import DoesNotExist

from .base import BaseRepository
from app.db.models import NotificationServiceRequest, NotificationService


class NotificationServiceName(str, Enum):
    TELEGRAM = 'telegram'
    EMAIL = 'email'
    PHONE = 'phone'


class NotificationServiceRepository(BaseRepository):
    model = NotificationService

    async def create(
            self,
            notification_service_request: NotificationServiceRequest,
    ):
        pass

    @staticmethod
    async def exist_service(name: str, value: str) -> bool:
        try:
            NotificationService.get((NotificationService.name == name) & (NotificationService.value == value))
            return True
        except DoesNotExist:
            return False
