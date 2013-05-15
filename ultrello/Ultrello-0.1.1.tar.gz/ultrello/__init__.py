import requests

# Input: username - A User's Trello username
#		 userOrg - Organization that the user belongs to
#		 userToken - Trello generated user Token
#		 APIkey - Trello API generated key
# Output: None
# Function: 
# Stores user specific information for use by the functions of the module


class TrelloUser(object):
	def __init__(self,username,userOrg,userToken,APIkey):
		self.username = username
		self.userOrg = userOrg
		self.userToken = userToken
		self.APIkey = APIkey

# Input: keyWordIn - (ex. boards,cards,member,etc.)
# 	   	 object_idIn - The ID property of the chosen keyword
#	   	 keyWord2In - (ex. boards,cards,member,etc.)
# Output: None
# Function: 
# Create and object to hold the properties for a given user.

	def create_url(self,keyWordIn,object_idIn,keyWord2In,object_idIn2):
		baseURLtest = 'https://api.trello.com/1/'
		keyWord = keyWordIn
		object_id = object_idIn
		keyWord2 = keyWord2In
		object_id2 = object_idIn2
		queryURL = baseURLtest + keyWord + '/' + object_id + '/' + keyWord2In
		return queryURL

# Input: None
# Output: List of names and ID's for all of a user's boards
# Function: 
# Creates the base URL for the query and defines query parameters. A
# call is made to obtain information for all boards. The names and ID's
# of the boards are displayed.

	def user_all_boards(self):
		request_obj = self.create_url('members',self.username,'boards','')
		payloadX = {'key':self.APIkey,'token':self.userToken,'filter':'all'}	
		allBoardsQuery = requests.get(request_obj,params=payloadX)
		allBoardsList = []
		allBoardsList = allBoardsQuery.json()
		allBoardsFinal = []
		for i in range(len(allBoardsList)):
			allBoardsFinal.append(allBoardsList[i]['name'])
			allBoardsFinal.append(allBoardsList[i]['id'])
		return allBoardsFinal

# Input: None
# Output: List of all cards the user is currently assigned to.
# Function:
# Creates the base URL for the query and defines query parameters. A
# call is made to obtain information for all cards a user is assigned to.
# The card names and board names are returned.

	def user_cards(self):
		request_obj = self.create_url('members',self.username,'actions','')
		payloadX = {'key':self.APIkey,'token':self.userToken}	
		userCardsQuery = requests.get(request_obj,params=payloadX)
		userCardsList = []
		userCardsList = userCardsQuery.json()
		userCardsFinal = []
		for i in range(len(userCardsList)):
			userCardsFinal.append(userCardsList[i]['data']['board']['name'])
			userCardsFinal.append(userCardsList[i]['data']['card']['name'])
		return userCardsFinal

# Input: dateIn - All cards SINCE this date
# Output: List of all cards the user is currently assigned to that have 
# 		  been created SINCE the given date
# Function:
# Creates the base URL for the query and defines query parameters. A
# call is made to obtain information for all cards a user is assigned to
# that have been created SINCE the given date.

	def user_cards_since(self,dateIn):
		date = dateIn
		request_obj = self.create_url('members',self.username,'actions','')
		payloadX = {'key':self.APIkey,'token':self.userToken,'since':date}	
		userCardsSinceQuery = requests.get(request_obj,params=payloadX)
		userCardsSinceList = []
		userCardsSinceList = userCardsSinceQuery.json()
		userCardsSinceFinal = []
		for i in range(len(userCardsSinceList)):
			userCardsSinceFinal.append(userCardsSinceList[i]['data']['board']['name'])
			userCardsSinceFinal.append(userCardsSinceList[i]['data']['card']['name'])
			userCardsSinceFinal.append(userCardsSinceList[i]['date'])
		return userCardsSinceFinal

# Input: dateIn - All cards BEFORE this date
# Output: List of all cards the user is currently assigned to that have 
# 		  been created BEFORE the given date
# Function:
# Creates the base URL for the query and defines query parameters. A
# call is made to obtain information for all cards a user is assigned to
# that have been created BEFORE the given date.

	def user_cards_before(self,dateIn):
		date = dateIn
		request_obj = self.create_url('members',self.username,'actions','')
		payloadX = {'key':self.APIkey,'token':self.userToken,'before':date}	
		userCardsBeforeQuery = requests.get(request_obj,params=payloadX)
		userCardsBeforeList = []
		userCardsBeforeList = userCardsBeforeQuery.json()
		userCardsBeforeFinal = []
		for i in range(len(userCardsBeforeList)):
			userCardsBeforeFinal.append(userCardsBeforeList[i]['data']['board']['name'])
			userCardsBeforeFinal.append(userCardsBeforeList[i]['data']['card']['name'])
			userCardsBeforeFinal.append(userCardsBeforeList[i]['date'])
		return userCardsBeforeFinal

# Input: user_obj - The passed in TrelloUser object allowing the Board 
#					class to use it's functions
#		 board_idIn - ID of the board to perform functions on
#		 name - Name of the board
# Output: None
# Function: 
# Stores board specific information for use by the functions of the module


class Board(object):

	def __init__(self,user_obj,board_idIn,name=''):
		self.user_obj = user_obj
		self.id = board_idIn
		self.name = name

# Input: None
# Output: List of names of lists in given board
# Function: 
# Creates the base URL for the query and defines query parameters. A
# call is made to obtain information for the given board. The names
# of all lists contained within the given board are returned.
	def all_lists(self):
		request_obj = self.user_obj.create_url('boards',self.id,'lists','')
		payloadX = {'key':self.APIkey,'token':self.userToken}	
		allListsQuery = requests.get(request_obj,params=payloadX)
		allListsList = []
		allListsList = allListsQuery.json()
		allListsFinal = []
		for i in range(len(allListsList)):
			allListsFinal.append(allListsList[i]['name'])
			allListsFinal.append(allListsList[i]['id'])

		return allListsFinal

# Input: None
# Output: List of all cards on given board
# Function: 
# Creates the base URL for the query and defines query parameters. A
# call is made to obtain information for the cards on given board. The names,
# ID's, and date of last activity are returned for each card on the board.

	def all_cards(self):
		request_obj = self.user_obj.create_url('boards',self.id,'cards','')
		payloadX = {'key':self.APIkey,'token':self.userToken,'filter':'all'}	
		allCardsQuery = requests.get(request_obj,params=payloadX)
		allCardsList = []
		allCardsList = allCardsQuery.json()
		allCardsFinal = []
		for i in range(len(allCardsList)):
			allCardsFinal.append(allCardsList[i]['name'])
			allCardsFinal.append(allCardsList[i]['id'])
			allCardsFinal.append(allCardsList[i]['dateLastActivity'])
		return allCardsFinal

# Input: None
# Output: List of all created cards, their names,list,dateOfCreation,creators name
# Function: 
# Creates the base URL for the query and defines query parameters. A
# call is made to obtain information for the created cards on given board. 
# This is used to obtain a list of card creation dates and who created them.

	def cards_created(self):
		request_obj = self.user_obj.create_url('boards',self.id,'actions','')
		payloadX = {'key':self.APIkey,'token':self.userToken,'filter':'idList,createCard'}	
		createdCardsQuery = requests.get(request_obj,params=payloadX)
		createdCardsList = []
		createdCardsList = createdCardsQuery.json()
		createdCardsFinal = []
		for i in range(len(createdCardsList)):
			createdCardsFinal.append(createdCardsList[i]['data']['card']['name'])
			createdCardsFinal.append(createdCardsList[i]['data']['list']['name'])
			createdCardsFinal.append(createdCardsList[i]['date'])
			createdCardsFinal.append(createdCardsList[i]['memberCreator']['fullName'])
		return createdCardsFinal

# Input: None
# Output: List of all board moves for a card. Returns nameOfCard,dateOfMove,listBefore,
#		  and listAfter.
# Function: 
# Creates the base URL for the query and defines query parameters. A
# call is made to obtain information for the move actions of the cards on given board. 
# This is used to obtain a list of card moves and where they moved to and from.

	def cards_moved(self):
		request_obj = self.user_obj.create_url('boards',self.id,'actions','')
		payloadX = {'key':self.APIkey,'token':self.userToken,'filter':'updateCard:idList'}	
		movedCardsQuery = requests.get(request_obj,params=payloadX)
		movedCardsList = []
		movedCardsList = movedCardsQuery.json()
		movedCardsFinal = []
		for i in range(len(movedCardsList)):
			movedCardsFinal.append(movedCardsList[i]['data']['card']['name'])
			movedCardsFinal.append(movedCardsList[i]['date'])
			movedCardsFinal.append("From:   " + movedCardsList[i]['data']['listBefore']['name'])
			movedCardsFinal.append("To:   " + movedCardsList[i]['data']['listAfter']['name'])
		return movedCardsFinal

# Input: None
# Output: List of all closed cards.
# Function: 
# Creates the base URL for the query and defines query parameters. A
# call is made to obtain information for the closed cards on given board. 
# This is used to obtain a list of closed cards and date in which they were closed.

	def all_closed(self):
		request_obj = self.user_obj.create_url('boards',self.id,'cards','')
		payloadX = {'key':self.APIkey,'token':self.userToken,'filter':'closed'}	
		closedCardsQuery = requests.get(request_obj,params=payloadX)
		closedCardsList = []
		closedCardsList = closedCardsQuery.json()
		closedCardsFinal = []
		for i in range(len(closedCardsList)):
			closedCardsFinal.append(closedCardsList[i]['name'])
			closedCardsFinal.append(closedCardsList[i]['id'])
			closedCardsFinal.append(closedCardsList[i]['dateLastActivity'])
		return closedCardsFinal

# Input: None
# Output: List of all open cards.
# Function: 
# Creates the base URL for the query and defines query parameters. A
# call is made to obtain information for all open cards on a given board. 
# This is used to obtain a list of all open cards on a list.		

	def all_open(self):
		request_obj = self.user_obj.create_url('boards',self.id,'cards','')
		payloadX = {'key':self.APIkey,'token':self.userToken,'filter':'open'}	
		openCardsQuery = requests.get(request_obj,params=payloadX)
		openCardsList = []
		openCardsList = openCardsQuery.json()
		openCardsFinal = []
		for i in range(len(openCardsList)):
			openCardsFinal.append(openCardsList[i]['name'])
			openCardsFinal.append(openCardsList[i]['id'])
		return openCardsFinal


# Input: None
# Output: The admins for a given board. Their name, id, and username.
# Function: To retrieve the members admin members of the given board.

	def get_admins(self):
		request_obj = self.user_obj.create_url('boards',self.id,'members','')
		payloadX = {'key':self.APIkey,'token':self.userToken,'filter':'admins'}	
		adminsQuery = requests.get(request_obj,params=payloadX)
		adminsList = []
		adminsList = adminsQuery.json()
		adminsFinal = []
		for i in range(len(adminsList)):
			adminsFinal.append(adminsList[i]['id'])
			adminsFinal.append(adminsList[i]['fullName'])
			adminsFinal.append(adminsList[i]['username'])
		return adminsFinal

# Input: boardNameIn - The name of the board 
#		 list_idIn - ID of the list to perform functions on
#		 nameIn - Name of the list
# Output: None
# Function: 
# Stores list specific information for use by the functions of the module		

class List(object):

	def __init__(self,user_objIn,boardNameIn,list_idIn,nameIn=''):
		self.user_obj = user_objIn
		self.boardName = boardNameIn
		self.id = list_idIn
		self.name = nameIn

# Input: None
# Output: List of all cards in desired list
# Function: To retrieve a list all cards in a given list

	def list_cards(self):
		request_obj = self.user_obj.create_url('lists',self.id,'cards','')
		payloadX = {'key':self.APIkey,'token':self.userToken}	
		listCardsQuery = requests.get(request_obj,params=payloadX)
		listCardsList = []
		listCardsList = listCardsQuery.json()
		listCardsFinal = []
		for i in range(len(listCardsList)):
			listCardsFinal.append(listCardsList[i]['name'])
			#listCardsFinal.append(listCardsList[i]['id'])
		return listCardsFinal

# Input: user_objIn - The passed in TrelloUser object allowing the Board 
#					  class to use it's functions
#		 card_idIn - ID of the card to perform functions on
#		 nameIn - Name of the card
# Output: None
# Function: 
# Stores card specific information for use by the functions of the module	

class Card(object):

	def __init__(self,user_objIn,card_id,name=''):
		self.user_obj = user_objIn
		self.id = card_id
		self.name = name

# Input: None
# Output: List of card specific information including name,url,
#		  idMembers,idShort,idBoard,labels
# Function: To retrieve card information from given card.

	def fetch(self):
		request_obj = self.user_obj.create_url('cards',self.id,'','')
		payloadX = {'key':self.APIkey,'token':self.userToken}	
		fetchCardsQuery = requests.get(request_obj,params=payloadX)
		fetchCardsList = []
		fetchCardsList = fetchCardsQuery.json()
		fetchCardsFinal = []
		fetchCardsFinal.append(fetchCardsList['name'])
		fetchCardsFinal.append(fetchCardsList['url'])
		fetchCardsFinal.append(fetchCardsList['idMembers'])
		fetchCardsFinal.append(fetchCardsList['idShort'])
		fetchCardsFinal.append(fetchCardsList['idBoard'])
		fetchCardsFinal.append(fetchCardsList['labels'])
		return fetchCardsFinal

# Input: None
# Output: The checklist for a given card
# Function: To retrieve the checklist for the given card.		

	def get_checklist(self):
		request_obj = self.user_obj.create_url('cards',self.id,'checklists','')
		payloadX = {'key':self.APIkey,'token':self.userToken}	
		checklistQuery = requests.get(request_obj,params=payloadX)
		checklistList = []
		checklistList = checklistQuery.json()
		checklistFinal = []
		checklistFinal.append(checklistList[0]['checkItems'])
		return checklistFinal
