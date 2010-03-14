

for x,y in (('three',3),('five',5)):
	print x
	print y
	print '---'

xs = [3,2,1]

xs.sort(lambda a,b : b-a)
print xs

for x in xs:
	if x == 5:
		xs.append(7)
	print x
