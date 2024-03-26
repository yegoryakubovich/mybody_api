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


from .account import AccountRepository
from .account_role import AccountRoleRepository
from .account_service import AccountServiceRepository
from .action import ActionRepository
from .country import CountryRepository
from .currency import CurrencyRepository
from .day import DayRepository
from .day_meal import DayMealRepository
from .day_training import DayTrainingRepository
from .image import ImageRepository
from .language import LanguageRepository
from .permission import PermissionRepository
from .role import RoleRepository
from .role_permission import RolePermissionRepository
from .session import SessionRepository
from .text import TextRepository
from .text_pack import TextPackRepository
from .text_translation import TextTranslationRepository
from .timezone import TimezoneRepository
from .article import ArticleRepository
from .article_translation import ArticleTranslationRepository
from .exercise import ExerciseRepository
from .meal import MealRepository
from .meal_product import MealProductRepository
from .meal_report import MealReportRepository
from .meal_report_image import MealReportImageRepository
from .meal_report_product import MealReportProductRepository
from .product import ProductRepository
from .service import ServiceRepository
from .service_cost import ServiceCostRepository
from .training import TrainingRepository
from .training_exercise import TrainingExerciseRepository
from .training_report import TrainingReportRepository
from .payment import PaymentRepository
from .payment_method import PaymentMethodRepository
from .payment_method_currency import PaymentMethodCurrencyRepository
from .promocode import PromocodeRepository
from .promocode_currency import PromocodeCurrencyRepository
from .url import UrlRepository
