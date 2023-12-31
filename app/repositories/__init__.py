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


from .account_role import AccountRoleRepository
from .account_service import AccountServiceRepository, AccountServiceStates
from .article import ArticleRepository
from .article_translation import ArticleTranslationRepository
from .exercise import ExerciseRepository
from .image import ImageRepository
from .meal import MealRepository
from .meal_product import MealProductRepository
from .meal_report import MealReportRepository
from .meal_report_image import MealReportImageRepository
from .meal_report_product import MealReportProductRepository
from .notification_service import NotificationServiceName, NotificationServiceRepository
from .notification_service_request import NotificationServiceRequestState, VerificationRequisiteType, \
    NotificationServiceRequestRepository
from .action import ActionRepository
from .account import AccountRepository
from .permission import PermissionRepository
from .product import ProductRepository
from .role import RoleRepository
from .role_permission import RolePermissionRepository
from .service import ServiceRepository
from .service_cost import ServiceCostRepository
from .session import SessionRepository
from .country import CountryRepository
from .language import LanguageRepository
from .text_translation import TextTranslationRepository
from .timezone import TimezoneRepository
from .currency import CurrencyRepository
from .text import TextRepository
from .text_pack import TextPackRepository
from .base import ModelDoesNotExist
from .training import TrainingRepository
from .training_exercise import TrainingExerciseRepository


__all__ = [
    'ActionRepository',
    'AccountRepository',
    'AccountServiceRepository',
    'AccountServiceStates',

    'SessionRepository',

    'CountryRepository',
    'LanguageRepository',
    'TimezoneRepository',
    'CurrencyRepository',
    'ImageRepository',

    'TextRepository',
    'TextTranslationRepository',
    'TextPackRepository',

    'ServiceRepository',
    'ServiceCostRepository',

    # Base
    'ModelDoesNotExist',

    # NotificationService
    'NotificationServiceName',
    'NotificationServiceRepository',

    # NotificationServiceRequest
    'NotificationServiceRequestState',
    'VerificationRequisiteType',
    'NotificationServiceRequestRepository',

    'RoleRepository',
    'AccountRoleRepository',
    'RolePermissionRepository',
    'PermissionRepository',

    'ArticleRepository',
    'ArticleTranslationRepository',

    'ProductRepository',

    'ExerciseRepository',
    'TrainingRepository',
    'TrainingExerciseRepository',

    'MealRepository',
    'MealProductRepository',
    'MealReportRepository',
    'MealReportImageRepository',
    'MealReportProductRepository',
]
