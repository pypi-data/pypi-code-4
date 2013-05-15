import ultrello
import requests

newUser = TrelloUser('username','org','userToken','APIKey')
newBoard = Board(newUser,'BoardID','BoardName')
newList = List(newUser,newBoard,'ListID','ListName')
newCard = Card(newUser,'CardID','CardName')


#Test for user_all_boards

testResult1 = newUser.user_all_boards()
for i in range(len(testResult1)):
	print testResult1[i]


#Test for user_cards

testResult2 = newUser.user_cards()
for i in range(len(testResult2)):
	print testResult2[i]


#Test for user_cards_since

testResult3 = newUser.user_cards_since('3/21/13')
for i in range(len(testResult3)):
	print testResult3[i]


#Test for user_cards_before

testResult4 = newUser.user_cards_before('3/21/13')
for i in range(len(testResult4)):
	print testResult4[i]


#Test for all_lists

testResult5 = newBoard.all_lists()
for i in range(len(testResult5)):
	print testResult5[i]


#Test for all_cards

testResult6 = newBoard.all_cards()
for i in range(len(testResult6)):
	print testResult6[i]


#Test for cards_moved

testResult7 = newBoard.cards_moved()
for i in range(len(testResult7)):
	print testResult7[i]


#Test for cards_created

testResult8 = newBoard.cards_created()
for i in range(len(testResult8)):
	print testResult8[i]


#Test for all_closed

testResult9 = newBoard.all_closed()
for i in range(len(testResult9)):
	print testResult9[i]


#Test for all_open

testResult10 = newBoard.all_open()
for i in range(len(testResult10)):
	print testResult10[i]


#Test for all_open

testResult11 = newBoard.get_admins()
for i in range(len(testResult11)):
	print testResult11[i]


#Test for list_cards

testResult12 = newList.list_cards()
for i in range(len(testResult12)):
	print testResult12[i]


#Test for list_cards

testResult13 = newCard.fetch()
for i in range(len(testResult13)):
	print testResult13[i]


#Test for get_checklist

testResult14 = newCard.get_checklist()
for i in range(len(testResult14)):
	for j in range(len(testResult14[i])):
		print testResult14[i][j]
