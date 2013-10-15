from datetime import datetime

for wo in rqliter('WorkOrder X WHERE X modification_date >= %(date)s',
                  {'date': datetime(2010, 10, 15)}).entities():
    wo.update_progress()
commit()
