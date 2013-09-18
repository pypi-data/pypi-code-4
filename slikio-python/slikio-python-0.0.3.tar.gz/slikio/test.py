import slikio

print "Testing\n"
slik =  slikio.SlikIO("prvkey_080618f6837fe75d8511")
col = 'col_3b057f15e4'

data = {
	"user": "Daniel",
	"email": "daniel@slik.io",
	"age": 17,
	"money": 1314
}

print slik.sendData(col, data).text
#should print {"success":"Data added to collection 5217670b9ddd8f1c57000001"}
