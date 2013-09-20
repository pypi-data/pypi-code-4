
import fixture

from rattail.db import model


class DepartmentData(fixture.DataSet):

    class grocery:
        number = 1
        name = 'Grocery'

    class supplements:
        number = 2
        name = 'Supplements'


def load_fixtures(engine):

    dbfixture = fixture.SQLAlchemyFixture(
        env={
            'DepartmentData': model.Department,
            },
        engine=engine)

    data = dbfixture.data(DepartmentData)

    data.setup()
