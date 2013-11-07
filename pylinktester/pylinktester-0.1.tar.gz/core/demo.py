import sys

reload(sys)
sys.setdefaultencoding("utf-8")

a = '中文'
print a.decode('gbk').encode(type)
print sys.getdefaultencoding()