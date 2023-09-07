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


from peewee import DoesNotExist

from app.db.models.base import BaseModel
from app.repositories import ActionRepository


class ModelDoesNotExist(Exception):
    pass


class BaseRepository:
    model: BaseModel
    model_name: str

    async def create_action(self, model: BaseModel, action: str, parameters: dict = None):
        await ActionRepository.create(
            model=self.model.__name__.lower(),
            model_id=model.id,
            action=action,
            parameters=parameters,
        )

    async def get_all(self) -> list[BaseModel]:
        return self.model.select().execute()

    async def get_by_name(self, name: str) -> BaseModel:
        try:
            return self.model.get(self.model.name == name)
        except DoesNotExist:
            raise ModelDoesNotExist(f'{self.model.__name__} "{name}" does not exist')
