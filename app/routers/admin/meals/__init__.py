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


from app.utils import Router
from .create import router as router_create
from .update import router as router_update
from .delete import router as router_delete
from .duplicate import router as router_duplicate
from .get import router as router_get
from .get_list import router as router_get_list
from .get_list_all import router as router_get_list_all
from .products import router as router_products
from .reports import router as router_reports


router = Router(
    prefix='/meals',
    tags=['Meals'],
    routes_included=[
        router_create,
        router_update,
        router_delete,
        router_duplicate,
        router_get,
        router_get_list,
        router_get_list_all,
        router_products,
        router_reports,
    ]
)
