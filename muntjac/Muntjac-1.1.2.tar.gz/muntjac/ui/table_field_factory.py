# Copyright (C) 2012 Vaadin Ltd. 
# Copyright (C) 2012 Richard Lincoln
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


class ITableFieldFactory(object):
    """Factory interface for creating new Field-instances based on Container
    (datasource), item id, property id and uiContext (the component responsible
    for displaying fields). Currently this interface is used by L{Table},
    but might later be used by some other components for L{Field}
    generation.

    @author: Vaadin Ltd.
    @author: Richard Lincoln
    @version: 1.1.2
    @see: FormFieldFactory
    """

    def createField(self, container, itemId, propertyId, uiContext):
        """Creates a field based on the Container, item id, property id and
        the component responsible for displaying the field (most commonly
        L{Table}).

        @param container:
                   the Container where the property belongs to.
        @param itemId:
                   the item Id.
        @param propertyId:
                   the Id of the property.
        @param uiContext:
                   the component where the field is presented.
        @return: A field suitable for editing the specified data or null if the
                property should not be editable.
        """
        raise NotImplementedError
