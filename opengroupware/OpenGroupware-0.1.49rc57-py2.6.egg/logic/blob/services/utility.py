#
# Copyright (c) 2013
#  Adam Tauno Williams <awilliam@whitemice.org>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#
from datetime import datetime

NAMESPACE_AUTOPRINT  = 'http://www.opengroupware.us/autoprint'
NAMESPACE_MANAGEMENT = '57c7fc84-3cea-417d-af54-b659eb87a046'

ATTRIBUTE_MANAGEMENT_COLLECTED = 'autoCollected'
ATTRIBUTE_MANAGEMENT_COLLECTION_DESC = 'autoCollectionDescriptor'

def get_inherited_property(context, folder, namespace, attribute):

    prop = context.property_manager.get_property( folder, namespace, attribute )

    if not prop:
        tmp = folder.folder
        while tmp:
            prop = context.property_manager.get_property( tmp, namespace, attribute )
            if prop:
                break
            tmp = tmp.folder

    if not prop:
        return None

    return prop.get_string_value( )


def expand_labels_in_name(value):

    if not value:
        return None

    today = datetime.today( )
    value = value.replace( '$__YEAR__;',       today.strftime( '%Y' ) )
    value = value.replace( '$__MONTH__;',      today.strftime( '%m' ) )
    value = value.replace( '$__DAYOFMONTH__;', today.strftime( '%d' ) )
    #value = value.replace( '$__WEEKOFMONTH__;', week_range_name_of_date( today ) )

    return value
