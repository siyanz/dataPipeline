import random, csv

node_count = 200
edge_count = 10000

nodes = []
edge = []

for i in range (0, edge_count):
	string = '{"source":' + str(random.randint(1, 76)) + ',"target":' + str(random.randint(1, 76)) + ',"value":' + str(random.randint(1, 31)) + '},'
	edge.append(string)

fp = open("data.csv", "a+")
writer = csv.writer(fp, delimiter='\n', escapechar='', quotechar='', quoting = csv.QUOTE_NONE)
writer.writerow(edge)