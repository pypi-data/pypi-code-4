#! /usr/bin/env python

gts = ['R', 'A', 'H']

family_size = 3

for idx1, gt1 in enumerate(gts):
	for idx2, gt2 in enumerate(gts):
		for idx3, gt3 in enumerate(gts):
			print gt1, gt2, gt3