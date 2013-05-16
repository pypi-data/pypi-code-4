"""函数名为printlb，参数两个，BM为列表名，SJ为缩进的TAB数，汤登奎制作发布"""
import sys
def printlb(bm,id=False,sj=0,fh=sys.stdout):
    """I为循环控制参数"""
    for i in bm:
        if isinstance(i,list):
            printlb(i,id,sj+1,fh)
        else:
            if id:
                for tab in range(sj):
                    print("\t",end='',file=fh)
            print(i,file=fh)
            
                      
