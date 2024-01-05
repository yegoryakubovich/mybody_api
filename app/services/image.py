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


from os import remove

from fastapi import File, UploadFile

from config import PATH_IMAGES
from .base import BaseService
from ..db.models import Image, Session
from ..repositories import ImageRepository
from ..utils import ApiException
from ..utils.crypto import create_id_str
from ..utils.decorators import session_required


class InvalidFileType(ApiException):
    pass


class TooLargeFile(ApiException):
    pass


class ImageService(BaseService):

    async def _create(
            self,
            session: Session,
            file: UploadFile,
            by_admin: bool = False,
    ) -> Image:
        id_str = await create_id_str()
        file_content = await file.read()

        action_parameters = {
            'creator': f'session_{session.id}',
            'id_str': id_str,
        }

        if by_admin:
            action_parameters.update(
                {
                    'by_admin': True,
                }
            )

        if file.content_type != 'image/jpeg':
            raise InvalidFileType('Invalid file type. Available: image/jpeg')

        if len(file_content) >= 16777216:
            raise TooLargeFile('Uploaded file is too large. Available size up to 16MB')

        with open(f'{PATH_IMAGES}/{id_str}.jpg', mode='wb') as image:
            image.write(file_content)
            image.close()

        image = await ImageRepository().create(id_str=id_str)

        await self.create_action(
            model=image,
            action='create',
            parameters=action_parameters
        )

        return image

    @session_required()
    async def create(
            self,
            session: Session,
            file: UploadFile = File(...),
    ):
        image = await self._create(file=file, session=session)

        return {'id_str': image.id_str}

    @session_required(permissions=['images'])
    async def create_by_admin(
            self,
            session: Session,
            file: UploadFile = File(...),
    ):
        image = await self._create(file=file, session=session)

        return {'id_str': image.id_str}

    @session_required(permissions=['images'])
    async def delete_by_admin(
            self,
            session: Session,
            id_str: str,
    ):
        image = await ImageRepository().get_by_id_str(id_str=id_str)

        await ImageRepository().delete(model=image)

        remove(f'{PATH_IMAGES}/{id_str}.jpg')

        await self.create_action(
            model=image,
            action='delete',
            parameters={
                'deleter': f'session_{session.id}',
                'id_str': id_str,
                'by_admin': True,
            },
        )

        return {}

    # @staticmethod  # FIXME
    # async def get_path(
    #         id_str: str,
    # ):
    #     return f'{PATH_IMAGES}/{id_str}.jpg'