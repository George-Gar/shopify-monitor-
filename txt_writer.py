import numpy as np

product_names = np.array(['Jordan', 'Nike', 'SB', 'Dunk', 'High', 'Vast',
	'Grey', 'Football', 'Vast-Grey', 'Football-Grey'])

for p in product_names:
	with open('undefeated.txt', 'a') as f:
		f.write(f'{p}\n')
		