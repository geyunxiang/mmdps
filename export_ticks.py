import json


def main():
	jfile = 'brodmann_lr_3.json'
	with open(jfile) as f:
		t = json.load(f)
	print(t['ticks'])
	with open('brodmann_ticks.csv', 'w') as f:
		for tick in t['ticks']:
			f.write(tick + '\n')
			
if __name__ == '__main__':
	main()
	print('end')
