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


from .account_parameter import AccountParameter
from .account_roles import AccountRole
from .action import Action
from .action_parameter import ActionParameter
from .article import Article
from .article_translation import ArticleTranslation
from .category_article import CategoryArticle
from .category_parameter_account import CategoryParameterAccount
from .language import Language
from .notification_services import NotificationService
from .notification_services_requests import NotificationServiceRequest
from app.db.models.text import Text
from app.db.models.text_translation import TextTranslation
from app.db.models.text_pack import TextPack
from .icons import Icon
from .country import Country
from .parameter_account import ParameterAccount
from .roles import Role
from .timezone import Timezone
from .currency import Currency
from .account import Account
from .session import Session


models = (
    Action,
    ActionParameter,

    Language,
    Text,
    TextTranslation,
    TextPack,
    Icon,
    Country,
    Timezone,
    Currency,
    Account,
    Session,

    NotificationService,
    NotificationServiceRequest,

    # AccountParameter
    CategoryParameterAccount,
    ParameterAccount,
    AccountParameter,

    CategoryArticle,
    Article,
    ArticleTranslation,

    Role,
    AccountRole,
)
