"""打印列表模块"""
def dylb(lbm,bz=False,sj=0):
    """代码段"""
    for jj in lbm:
        if isinstance(jj,list):
            dylb(jj,bz,sj+1)
        else:
            if bz:
                
                for tt in range(sj):
                    print("\t",end='')
            print(jj)

        
