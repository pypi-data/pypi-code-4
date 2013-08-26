# -*- coding: utf-8 -*-
"""
``pybill.lib.errors`` module contains the specific exceptions that can be raised
during a PyBill run.

.. autoexception:: PyBillException
   :members:
   :undoc-members:
   :show-inheritance: 

.. autoexception:: PyBillReadingException
   :members:
   :undoc-members:
   :show-inheritance: 

.. autoexception:: PyBillWritingException
   :members:
   :undoc-members:
   :show-inheritance: 

.. autoexception:: PyBillProcessingException
   :members:
   :undoc-members:
   :show-inheritance: 
"""
__docformat__ = "restructuredtext en"


class PyBillException(Exception):
    """
    Base class of the exceptions raised by PyBill.
    """
    pass

class PyBillReadingException(PyBillException):
    """
    Exception raised when an error occurs during reading.
    """
    pass

class PyBillWritingException(PyBillException):
    """
    Exception raised when an error occurs during writing.
    """
    pass

class PyBillProcessingException(PyBillException):
    """
    Exception raised when an error occurs during processing.
    """
    pass
