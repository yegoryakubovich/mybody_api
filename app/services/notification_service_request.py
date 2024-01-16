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
from random import randint

from pytz import UTC

from app.db.models import NotificationServiceRequest, Session
from app.repositories import VerificationRequisiteType, NotificationServiceRequestState, \
    NotificationServiceRequestRepository
from app.repositories.account import AccountRepository
from app.repositories.notification_service import NotificationServiceRepository, NotificationServiceName
from app.services.base import BaseService
from app.utils.exceptions import ApiException
from app.utils.crypto import create_salt, create_hash_by_string_and_salt
from app.utils.decorators import session_required
from config import TG_BOT_USERNAME


class NotificationServiceExist(ApiException):
    pass


class NotificationServiceNameInAccountExist(ApiException):
    pass


class NotificationServiceNameInDevelop(ApiException):
    pass


class VerificationRequisite:
    verification_type: VerificationRequisiteType
    value: int | str

    def __init__(self, verification_type: VerificationRequisiteType, value: str | int):
        self.verification_type = verification_type
        self.value = value


class NotificationServiceRequestService(BaseService):
    @session_required()
    async def create(
            self,
            session: Session,
            name: str,
            value: str,
    ) -> (NotificationServiceRequest, VerificationRequisite):
        account = session.account

        # Checking for the presence of such services (only value) on all accounts (for phone and email)
        if (
                name in [
                    NotificationServiceName.PHONE,
                    NotificationServiceName.EMAIL,
                ] and
                await NotificationServiceRepository.exist_service(name=name, value=value)
        ):
            raise NotificationServiceExist(
                f'{name.capitalize()} ({value}) notification service already connected to account'
            )

        # Checking for the presence of services on current account
        if name in await AccountRepository.get_notification_services(
                account=account, only_names=True
        ):
            raise NotificationServiceNameInAccountExist(
                f'{name.capitalize()} notification service already connected to this account',
            )

        if name in [NotificationServiceName.PHONE, NotificationServiceName.EMAIL]:
            raise NotificationServiceNameInDevelop(
                f'{name.capitalize()} notification service in development',
            )

        verification = str(randint(100000, 999999))
        verification_salt = await create_salt()
        verification_hash = await create_hash_by_string_and_salt(string=verification, salt=verification_salt)
        verification_expired_datetime = datetime.now(tz=UTC) + timedelta(minutes=15)
        verification_can_repeat_datetime = datetime.now(tz=UTC) + timedelta(minutes=1)
        state = NotificationServiceRequestState.WAITING

        # Create request and action
        notification_service_request = await NotificationServiceRequestRepository().create(
            account=account,
            name=name,
            verification_salt=verification_salt,
            verification_hash=verification_hash,
            verification_expired_datetime=verification_expired_datetime,
            verification_can_repeat_datetime=verification_can_repeat_datetime,
            state=state,
        )
        await self.create_action(
            model=notification_service_request,
            action='create',
            parameters={
                'creator': f'session_{session.id}',
                'name': name,
                'verification_expired_datetime': verification_expired_datetime,
                'verification_can_repeat_datetime': verification_can_repeat_datetime,
                'state': state,
            },
        )

        verification_requisite = VerificationRequisite(
            verification_type=VerificationRequisiteType.URL,
            value=f'https://t.me/{TG_BOT_USERNAME}?start={notification_service_request.id}:{verification}',
        )

        return verification_requisite.__dict__
