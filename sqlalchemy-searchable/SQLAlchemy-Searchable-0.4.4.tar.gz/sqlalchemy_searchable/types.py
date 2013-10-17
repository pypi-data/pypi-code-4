import sqlalchemy as sa
from sqlalchemy_utils import TSVectorType
from sqlalchemy_utils.functions import has_changed


class CompositeTSVectorType(sa.types.TypeDecorator):
    impl = TSVectorType

    def __init__(self, attr_paths):
        attr_paths = attr_paths
        sa.types.TypeDecorator.__init__(self)


def search_vectors(obj):
    for property_ in sa.inspect(obj).iterate_properties:
        if (
            isinstance(property_, sa.orm.ColumnProperty) and
            isinstance(property_.columns[0].type, TSVectorType)
        ):
            return property_.columns[0].key


def has_changed_search_vector(obj):
    """
    Returns whether or not the search vector columns of given SQLAlchemy
    declarative object have changed.

    :param obj: SQLAlchemy declarative model object
    """
    for vector in search_vectors(obj):
        for column_name in vector.type.columns:
            if has_changed(obj, column_name):
                return True
    return False


def vector_agg(vector):
    return sa.sql.expression.cast(
        sa.func.coalesce(
            sa.func.array_to_string(sa.func.array_agg(vector), ' ')
        ),
        TSVectorType
    )
