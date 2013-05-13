#!-*-coding: utf8-*-

import urllib2
from bs4 import BeautifulSoup
from bs4 import UnicodeDammit

count = 0 #마지막에 넘어간 페이지 수를 체크 할 것이다.
ErrorCount = 0 #마지막에 url에러가 발생한 수를 체크 할 것이다.
CID = ["73222","32206","80274","71986","85109","70126","72018","71966","71968"] #유아서적은 주제별로 7가지로 나뉜다.

for each_cid in CID:

    url = "http://www.aladin.co.kr/shop/common/wbest.aspx?BranchType=1&CID="+str(each_cid)+"&Year=2013&Month=4&Week=5" #주제별 베스트셀러페이지
    page = urllib2.urlopen(url)
    soup = BeautifulSoup(page, from_encoding="euc-kr") #기본 인코딩은 euc-kr
    #print soup.original_encoding #인코딩 확인용

    findISBN = soup.find_all(name="a",attrs={"class":"bo3"})  #주제별 모든 베스트셀러들의 ISBN(key)을 받아온다.

    isbnList = [] #ISBN목록을 담을 리스트 생성
    for each_ISBN in findISBN:
        isbn = []
        isbnSet = []
        if(each_ISBN != None):
            for i in range(69,79):     #ISBN이 있는 범위 선택
                isbn.append(str(each_ISBN)[i])  #숫자 하나 하나 가져온다.
            isbnSet = (isbn[0]+isbn[1]+isbn[2]+isbn[3]+isbn[4]+isbn[5]+isbn[6]+isbn[7]+isbn[8]+isbn[9]) #숫자를 합쳐서 ISBN완성
            
        isbnList.append(isbnSet)  #ISBN을 리스트로 저장한다.
    #print isbnList     #ISBN리스트 확인

    for each_isbn in isbnList:   #각 ISBN별, CID별로 리뷰를 저장할 파일을 만든다.
        f = open('201345CID'+str(each_cid)+'ISBN'+str(each_isbn)+'.txt','w')
        for each_page in range(1,50):   #각 ISBN별, 페이지별로 리뷰를 불러온다. 페이지가 적더라도 100페이지까지 읽게하는 부분이 비효율적임..
            try:
                 url = "http://www.aladin.co.kr/shop/common/wbook_talktalk.aspx?page="\
                       +str(each_page)+"&ISBN="+str(each_isbn)+"&CommunityType=MyReview&SortOrder=&IsOrderer=2"
                 page = urllib2.urlopen(url)
            except (ValueError,urllib2.URLError) as e:
                print (e)
                ErrorCount = ErrorCount + 1
                pass
        
            soup = BeautifulSoup(page, from_encoding="cp949")
            print soup.original_encoding  #기본 인코딩 확

            if(soup.original_encoding != "cp949"):   #기본인코딩이 euc-kr로 변환이 안되고, windows-1252로 그대로 있으면 페이지넘어감.
                count = count + 1
                pass

            else:
                findReview = soup.find_all(name="dd",attrs={"class":"npd_spacet10"})

                for each_review in findReview:
                    if(each_review != None):
                        Review = each_review.text.encode("utf-8").strip()
                        print Review
                        f.write(Review+'\n')
            
        f.close()    #파일을 닫는다.

print ("인코딩 문제로 넘어간 페이지 수 : "+str(count))
print ("urlopen에러 개수 : "+str(ErrorCount))

