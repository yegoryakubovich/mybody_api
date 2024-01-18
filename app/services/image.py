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


from os import path, remove

from fastapi import UploadFile
from PIL import Image as ImagePillow

from config import PATH_IMAGES
from .base import BaseService
from ..db.models import Image, Session
from ..repositories import ImageRepository
from ..utils.crypto import create_id_str
from ..utils.decorators import session_required


class ImageService(BaseService):
    async def _create(
            self,
            session: Session,
            file: UploadFile,
            by_admin: bool = False,
    ) -> Image:
        id_str = await create_id_str()

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

        with open(f'{PATH_IMAGES}/{id_str}.jpg', mode='wb') as image:
            file_content = await file.read()
            image.write(file_content)
            image.close()

        while path.getsize(f'{PATH_IMAGES}/{id_str}.jpg') > 2097152:
            image = ImagePillow.open(f'{PATH_IMAGES}/{id_str}.jpg')

            width, height = image.size
            new_size = (int(width // 1.5), int(height // 1.5))
            resized_image = image.resize(new_size)

            resized_image.save(f'{PATH_IMAGES}/{id_str}.jpg', optimize=True, quality=90)

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
            file: UploadFile,
            return_model: bool = False,
    ):
        image = await self._create(file=file, session=session)

        if return_model:
            return image

        return {'id_str': image.id_str}

    @session_required(permissions=['images'])
    async def create_by_admin(
            self,
            session: Session,
            file: UploadFile,
            return_model: bool = False,
    ):
        image = await self._create(file=file, session=session)

        if return_model:
            return image

        return {'id_str': image.id_str}

    async def _delete(
            self,
            session: Session,
            id_str: str,
            by_admin: bool = False,
    ):
        image = await ImageRepository().get_by_id_str(id_str=id_str)

        action_parameters = {
            'deleter': f'session_{session.id}',
            'id_str': id_str,
        }

        if by_admin:
            action_parameters.update(
                {
                    'by_admin': True,
                }
            )

        await ImageRepository().delete(model=image)

        remove(f'{PATH_IMAGES}/{id_str}.jpg')

        await self.create_action(
            model=image,
            action='delete',
            parameters=action_parameters,
        )

        return {}

    @session_required()
    async def delete(
            self,
            session: Session,
            id_str: str,
    ):
        return await self._delete(
            session=session,
            id_str=id_str,
        )

    @session_required(permissions=['images'])
    async def delete_by_admin(
            self,
            session: Session,
            id_str: str,
    ):
        return await self._delete(
            session=session,
            id_str=id_str,
            by_admin=True,
        )
