import json


def create_brodmann_ticks():
	regions = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 32, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 82, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98]
	ticks = []
	for i in range(41):
		region = regions[i]
		ticks.append('L'+str(region))
	for i in range(41):
		region = regions[41+i]
		ticks.append('R'+str(region-50))
	return ticks
		

def create_aal_ticks():
	ticks = []
	for i in range(116):
		r = i + 1
		#ticks.append(('L' if r%2==1 else 'R') + str(r))
		ticks.append(('AL' if r%2==1 else 'AR') + str(r))
	return ticks
	
def create_aal_order():
	orderl = list(range(0, 116, 2))
	orderr = list(range(1, 116, 2))
	orderl.extend(orderr)
	return orderl

	 
if __name__ == '__main__':
	ticks = create_brodmann_ticks()
	print('Brodmann lr ticks')
	print(json.dumps(ticks))

	ticks = create_aal_ticks()
	print('AAL ticks')
	print(json.dumps(ticks))
		
	order = create_aal_order()
	print('AAL order')
	print(json.dumps(order))
