
##from test import printlist
import test

print('*********利用模块导入***********')
Films = ["Ljrfox", 21, "TeenStian", 22, 'Tornado', 23, "Moxmen", 24,
         ["Beijing", "Changsha", 'Shenzhen', ['IT', "Book", 'Star']]]
test.printlist(Films)
print("***********************")

print('*********range方法***********')
for num in range(4):
    print(num)
print("***********************")

print('*********新函数***********')
def printnewlist(List, indent=False, nTab=0):
    for ListMem in List:
        if isinstance(ListMem, list):
            printnewlist(ListMem, indent, nTab+1)
        else:
            if indent:
                for num in range(nTab):
                    print('\t', end='')
            print(ListMem)
print("***********************")

print('*********调用新函数***********')
printnewlist(Films, True, 4)
print("***********************")
