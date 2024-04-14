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
from os.path import isfile

from fastapi import Depends
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from app.utils import Router
from app.utils.exceptions import ModelDoesNotExist

router = Router(
    prefix='/{filename}',
)


class DocsGetSchema(BaseModel):
    filename: str = Field()


@router.get()
async def route(schema: DocsGetSchema = Depends()):
    if not isfile(f'assets/docs/{schema.filename}'):
        raise ModelDoesNotExist(
            kwargs={
                'model': 'file',
                'id_type': 'name',
                'id_value': schema.filename,
            }
        )
    return FileResponse(
        path=f'assets/docs/{schema.filename}',
    )
