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


from datetime import datetime, timedelta

from peewee import DoesNotExist

from app.db.models import Request
from app.repositories.base import BaseRepository
from app.utils.exceptions import ModelAlreadyExist


class RequestRepository(BaseRepository):
    model = Request

    async def create(self, **kwargs):
        try:
            phone = kwargs.get('phone')
            request = Request.get(
                (Request.phone == phone)
            )
            if datetime.utcnow()-request.created_at < timedelta(hours=1):
                raise ModelAlreadyExist(
                    kwargs={
                        'model': 'Request',
                        'id_type': 'phone',
                        'id_value': phone,
                    },
                )
            else:
                return await super().create(**kwargs)
        except DoesNotExist:
            return await super().create(**kwargs)
