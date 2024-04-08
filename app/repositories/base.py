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


from peewee import DoesNotExist

from app.db.models.base import BaseModel
from app.utils.exceptions import ModelDoesNotExist, ModelAlreadyExist


class BaseRepository:
    model: BaseModel
    model_name: str

    def __init__(self, model: BaseModel = None):
        if model:
            self.model = model

    async def is_exist(self, id_: str) -> bool:
        try:
            self.model.get((self.model.id == id_) & (self.model.is_deleted == False))
            return True
        except DoesNotExist:
            return False

    async def is_exist_by_id_str(self, id_str: str) -> bool:
        try:
            self.model.get((self.model.id_str == id_str) & (self.model.is_deleted == False))
            return True
        except DoesNotExist:
            return False

    async def create(self, **kwargs):
        if 'id_str' in kwargs.keys():
            id_str = kwargs.get('id_str')
            try:
                await self.get_by_id_str(id_str=id_str)
                raise ModelAlreadyExist(
                    kwargs={
                        'model': self.model.__class__.__name__,
                        'id_type': 'id_str',
                        'id_value': id_str,
                    },
                )
            except ModelDoesNotExist:
                pass

        return self.model.create(**kwargs)

    async def get_list(self) -> list[BaseModel]:
        return self.model.select().where(self.model.is_deleted == False).execute()

    async def get_by_id(self, id_: int) -> BaseModel:
        try:
            model = self.model.get(
                (self.model.id == id_) &
                (self.model.is_deleted == False)
            )
            return model
        except DoesNotExist:
            raise ModelDoesNotExist(
                kwargs={
                    'model': self.model.__name__,
                    'id_type': 'id',
                    'id_value': id_,
                },
            )

    async def get_by_id_str(self, id_str: str) -> BaseModel:
        try:
            self.model = self.model.get(
                (self.model.id_str == id_str) &
                (self.model.is_deleted == False)
            )
            return self.model
        except DoesNotExist:
            raise ModelDoesNotExist(
                kwargs={
                    'model': self.model.__name__,
                    'id_type': 'id_str',
                    'id_value': id_str,
                },
            )

    @staticmethod
    async def update(model, **kwargs):
        for key, value in kwargs.items():
            if key[-1] == '_':
                key = key[:-1]
            if value:
                if isinstance(value, int) and value == -1:
                    exec(f'model.{key} = None')
                else:
                    exec(f'model.{key} = value')
            elif isinstance(value, bool) and value == False:
                exec(f'model.{key} = False')
            elif isinstance(value, bool) and value == True:
                exec(f'model.{key} = True')
        model.save()

    @staticmethod
    async def delete(model: BaseModel) -> BaseModel:
        model.is_deleted = True
        model.save()
        return model
