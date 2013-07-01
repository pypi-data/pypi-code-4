"""打印列表模块"""
def dylb(lbm):
    """代码段"""
    for jj in lbm:
        if isinstance(jj,list):
            dylb(jj)
        else:
            print(jj)

        
