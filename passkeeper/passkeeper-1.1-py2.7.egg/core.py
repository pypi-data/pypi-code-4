#! /usr/bin/env python
# -*- coding: utf-8 -*-

#author:gaoda
#date:2012.7.30
#filename:passkeeper.core
#descirbe:a keeper for your all kinds of password
#spilt using tab

from sqlalchemy import *
from sqlalchemy.orm import *
import string
import sys
import argparse
from pkg_resources import resource_stream

'''init the sqlite database'''
#with resoure_stream(__name__,'pwddb.db') as db 
class pwd(object):
	'''the class contect with database tables'''
	def _init_(self,where,user,pwd):
		self.where=where
		self.user=user
		self.pwd=pwd
		
engine = create_engine('sqlite:///pwddb.db')
metadata=MetaData(engine)
pwd_table=Table(
	'gaodapwd',metadata,
	Column('where',String,primary_key=True),
	Column('user',String),
	Column('pwd',String)
	)
metadata.create_all(engine)
mapper(pwd,pwd_table)	
session=sessionmaker(bind=engine)
session=create_session()


'''define the basic operations'''

def look():
	record = []
	i=0
	for temp in session.query(pwd).all():
		record.append([temp.where,temp.user,temp.pwd])
		i=1
	if i==0:
		record.append("empty")
	return record

def add(new_record):
	temp=pwd()
	temp.where = new_record[0]
	temp.user = new_record[1]
	temp.pwd = new_record[2]
	try:
		session.add(temp)
		session.flush()
		return True
	except:
		return False

def delete(del_place):
	temp_where=del_place
	sign=0
	for temp_pwd in session.query(pwd).filter_by(where=temp_where).all():
		sign=sign+1
		session.delete(temp_pwd)
	session.flush()		
	return sign

def perfect_info(add_list):
	'''test the input format when add new record'''
	i=0
	context=[]
	string = str(add_list)
	for value in string.split(','):
		i=i+1
		context.append(value)
	if i!=3:
		msg="input error eg'where,username,password'"
		raise argparse.ArgumentTypeError(msg)
	return context

def main():
	parser = argparse.ArgumentParser(description='keep password and username',prog='PROG')
	parser.add_argument('-look',action="store_true",dest='look',help='look the user and pass word now exicted')
	parser.add_argument('-add',type=perfect_info,dest='add',help='add the new records')
	parser.add_argument('-del',dest='delete',help='del the record useing the "where"')
	
	args = parser.parse_args()
	
	if args.look:
		records=look()
		if records[0]=="empty":
			sys.stdout.write("empty\n")
		else:
			for record in records:	
				sys.stdout.write(record[0])
				sys.stdout.write("   ")
				sys.stdout.write(record[1])
				sys.stdout.write("   ")
				sys.stdout.write(record[2])
				sys.stdout.write("\n")
		sys.exit(0)
	if args.add:
		context = perfect_info(args.add)
		sign = add(context)
		if sign:
			sys.stdout.write("add succeful\n")
			sys.exit(0)
		else:
			sys.stdout.write("add faild\n")
			sys.exit(1)
	if args.delete:
		sign = delete(args.delete)
		if sign:
			sys.stdout.write("delete succeful\n")
			sys.exit(0)
		else:	
			sys.stdout.write("delete faild\n")
			sys.exit(1)

if __name__=="__main__":
	main()		
