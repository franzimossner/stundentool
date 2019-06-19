from models import Datasheet
from table import Table
from table.columns import Column

class DataTable(Table):
    id = Column(field='id')
    name = Column(field='name')
    class Meta:
        model = Datasheet
