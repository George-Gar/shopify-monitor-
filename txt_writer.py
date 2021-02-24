import numpy as np

product_names = np.array(['Jordan', 'Nike',
                          'Nike Air Jordan 12 Retro Low SE', 'Navy', 'III', 'Rider', 'Zoom Freak'])

for p in product_names:
	with open('shoe_palace.txt', 'a') as f:
		f.write(f'{p}\n')
		