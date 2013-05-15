"""函数名为printlb，参数两个，BM为列表名，SJ为缩进的TAB数，汤登奎制作发布"""
def printlb(bm,sj):
    """I为循环控制参数"""
    for i in bm:
        if isinstance(i,list):
            printlb(i,sj+1)
        else:
            for tab in range(sj):
                print("\t",end='')
            print(i)
                      
