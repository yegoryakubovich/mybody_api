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


from app.db.models import Session
from app.repositories import TimezoneRepository
from app.services.base import BaseService
from app.utils.decorators import session_required


class TimezoneService(BaseService):
    @session_required()
    async def create(
            self,
            session: Session,
            id_str: str,
            deviation: int,
    ):
        timezone = await TimezoneRepository().create(
            id_str=id_str,
            deviation=deviation
        )

        await self.create_action(
            model=timezone,
            action='create',
            parameters={
                'creator': f'session_{session.id}',
                'id_str': timezone.id_str,
                'deviation': timezone.deviation,
            },
            with_client=True,
        )

        return {'id_str': timezone.id_str}

    @session_required()
    async def delete(
            self,
            session: Session,
            id_str: str,
    ):
        timezone = await TimezoneRepository().get_by_id_str(id_str=id_str)
        await TimezoneRepository().delete(model=timezone)

        await self.create_action(
            model=timezone,
            action='delete',
            parameters={
                'deleter': f'session_{session.id}',
                'id_str': id_str,
            }
        )

        return {}

    @staticmethod
    async def get(
            id_str: str,
    ):
        timezone = await TimezoneRepository().get_by_id_str(id_str=id_str)
        return {
            'timezone': {
                'id': timezone.id,
                'id_str': timezone.id_str,
                'deviation': timezone.deviation,
            }
        }

    @staticmethod
    async def get_list() -> dict:
        timezones = {
            'timezones': [
                {
                    'id': timezone.id,
                    'id_str': timezone.id_str,
                    'deviation': timezone.deviation
                }
                for timezone in await TimezoneRepository().get_list()
            ],
        }
        return timezones
