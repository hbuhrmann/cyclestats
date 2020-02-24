import numpy
import pandas

def evenDigitsOnly(n):
	charlist=list(str(n))
	digits = pandas.Series(charlist)
	output1 = ((numpy.mod(digits.astype(float), 2)))
	#output = ((numpy.mod(digits,2)==0)*1)
	#sumtotal = output.sum()
	print (digits.astype(float),output1.sum())



evenDigitsOnly(24678)
