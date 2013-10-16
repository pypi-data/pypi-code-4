"""
This package provides an AlarmServer class which is able to handle
alarms. It is intended for HMI software where alarm handling is often
necessary.

The following features are provided:
    - defining alarms with numbers and alarm texts
    - alarms are handled and identified by their alarm number
    - alarms can come and leave
    - alarms can be acknowledged and cleared by the user

In addition to the basic AlarmServer class there is an AlarmServerModel
class which implements the model/view pattern used by the Qt framework.
So this class can be used as a model for QTableView or QListView.
"""

from alarmserver import AlarmServer, Alarm, AlarmWord