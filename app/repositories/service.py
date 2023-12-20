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


from app.db.models import Service, Text
from .base import BaseRepository
from app.utils import ApiException


class NoRequiredParameters(ApiException):
    pass


class ServiceRepository(BaseRepository):
    model = Service

    @staticmethod
    async def create(
            id_str: str,
            name_text: Text,
            questions: str = None,
    ):
        return Service.create(
            id_str=id_str,
            name_text=name_text,
            questions=questions,
        )

    @staticmethod
    async def update(
            service: Service,
            name: str = None,
            questions: str = None,
    ):
        if questions:
            service.questions = questions
        if not name and not questions:
            raise NoRequiredParameters('One of the following parameters must be filled in: name, questions')
        service.save()
