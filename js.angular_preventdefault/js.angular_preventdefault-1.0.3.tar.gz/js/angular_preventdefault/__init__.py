import js.angular
from fanstatic import Library, Resource

library = Library('angular-prevent-default', 'resources')

angular_prevent_default = Resource(
    library, 'angular-prevent-default.js', depends=[js.angular.angular])

