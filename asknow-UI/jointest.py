def joinfunc(array):
	a = []
	a.append(', '.join(array[0:-1]))
	a.append(array[-1])
	return ' and '.join(a)
	
print joinfunc(['Berlin', 'New Delhi'])
# Berlin and New Delhi
print joinfunc(['Berlin', 'New Delhi', 'Washington D.C.'])
# Berlin, New Delhi and Washington D.C.
print joinfunc(['Berlin', 'New Delhi', 'Washington D.C.', 'Paris'])
# Berlin, New Delhi, Washington D.C. and Paris