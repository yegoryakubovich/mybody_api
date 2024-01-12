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


from .account import Account
from .account_role import AccountRole
from .account_service import AccountService
from .action import Action
from .action_parameter import ActionParameter
from .article import Article
from .article_translation import ArticleTranslation
from .billing import Billing
from .exercise import Exercise
from .image import Image
from .language import Language
from .meal import Meal
from .meal_product import MealProduct
from .meal_report import MealReport
from .meal_report_image import MealReportImage
from .meal_report_product import MealReportProduct
from .notification_services import NotificationService
from .notification_services_requests import NotificationServiceRequest
from .permission import Permission
from .product import Product
from .role_permission import RolePermission
from .text import Text
from .text_translation import TextTranslation
from .text_pack import TextPack
from .country import Country
from .role import Role
from .service import Service
from .service_cost import ServiceCost
from .timezone import Timezone
from .currency import Currency
from .session import Session
from .training import Training
from .training_exercise import TrainingExercise
from .training_report import TrainingReport

models = (
    Action,
    ActionParameter,

    Language,
    Text,
    Image,
    TextTranslation,
    TextPack,
    Country,
    Timezone,
    Currency,
    Account,
    Session,

    NotificationService,
    NotificationServiceRequest,

    Service,
    ServiceCost,
    AccountService,
    Billing,

    # Articles
    Article,
    ArticleTranslation,

    # Roles & permissions
    Role,
    Permission,
    RolePermission,
    AccountRole,

    Product,

    Exercise,
    Training,
    TrainingExercise,
    TrainingReport,

    Meal,
    MealProduct,
    MealReport,
    MealReportProduct,
    MealReportImage,
)
