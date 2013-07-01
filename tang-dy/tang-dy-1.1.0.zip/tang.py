"""打印列表模块"""
def dylb(lbm,sj):
    """代码段"""
    for jj in lbm:
        if isinstance(jj,list):
            dylb(jj,sj+1)
        else:
            for tt in range(sj):
                print("\t",end='')
            print(jj)

        
