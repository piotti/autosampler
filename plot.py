from matplotlib import pyplot as plt

data = [[] for i in range(7)]
for lnum, l in enumerate(open('20H16M.txt').readlines()):
	# print([x for x in l.split(' ') if x.strip()])
	# break
	# print(lnum)
	for i, e in enumerate([x for x in l.split(' ') if x.strip()]):
		# print(i)
		data[i].append(e)

print([len(data[i]) for i in range(7)])

plt.plot(data[0][:100], data[2][:100])

plt.show()