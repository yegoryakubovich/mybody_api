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
from datetime import datetime

from .base import BaseService
from app.repositories import RequestRepository
from ..utils import TelegramNotification


class RequestService(BaseService):
    async def create(
            self,
            phone: str,
            name: str,
    ):
        request = await RequestRepository().create(
            phone=phone,
            name=name,
            created_at=datetime.utcnow(),
        )

        await self.create_action(
            model=request,
            action='create',
            parameters={
                'phone': phone,
            }
        )

        await TelegramNotification().new_request(phone=phone, name=name)

        return {}
