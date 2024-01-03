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


class MealTypes:
    BREAKFAST = 'breakfast'
    SNACK_1 = 'snack_1'
    LUNCH = 'lunch'
    SNACK_2 = 'snack_2'
    DINNER = 'dinner'

    def all(self):
        return [self.BREAKFAST, self.SNACK_1, self.LUNCH, self.SNACK_2, self.DINNER]
