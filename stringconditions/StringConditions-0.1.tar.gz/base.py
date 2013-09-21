import re


class StringConditionsException( Exception ):
	pass


def array_has_any( any, array ):
	matched = False
	for a in any:
		if a in array:
			matched = True
	return matched


def array_has_all( all, array ):
	for a in all:
		if a not in array:
			return False
	return True


def remove_values_from_list( the_list, val ):
	return [value for value in the_list if value != val]


def compute_or( condition, values ):
	#	We got an OR operator. At least one must match
	a_any = condition.split( "|" )

	if "&" not in condition and not array_has_any( a_any, values ):
		raise StringConditionsException(
			"At least one value from ({}) must be provided".format(
				"|".join( a_any ) ) )
	elif "&" in condition:
		#	The OR condition contains an AND
		for a in a_any:
			if "&" in a:
				compute_and( condition, a )


def compute_and( condition, values ):
	a_and_condition = condition.split( "&" )

	#	Everything that is bounded by & must be present IF ANY is present
	for and_condition in a_and_condition:
		if "|" not in and_condition:
			if and_condition not in values:
				raise StringConditionsException(
					"The following values must be present: `{0}`".format(
						", ".join( a_and_condition ) ) )
		else:
			compute_or( and_condition, values )


def validate( condition, values ):
	#	Split by whitespace but only if it's not
	#	between parenthesis, accolades or squared bracckets
	#	I only got ideas for parenthesis and I don't know
	#	why the fuck I consider accolades and squareds but who knows
	a_condition = re.compile( "\s+(?![^\[]*\]|[^(]*\)|[^\{]*})" ).split( condition )

	for c in a_condition:
		if not c.startswith( "(" ):
			if not "|" in c and not "&" in c:
				#	Simple condition matched, check
				#	if it's present in values list
				if not c in values:
					raise StringConditionsException(
						"`{}` is a required value".format( c ) )
			elif "|" in c:
				compute_or( c, values )
			elif "&" in c:
				compute_and( c, values )
		else:
			#	We got parenthesis which means only one
			#	from the provided values must be present
			#	ex: (red blue green). Similar to OR but with OR
			#	all values can be present
			c = c[1:-1]
			exists_counter = 0
			a_exclusive = c.split( " " )

			for exclusive in a_exclusive:
				if "&" in exclusive:
					try:
						#	If we get an error out of here it means
						#	that not all values are present. If exception
						#	is thrown no counter is incremented
						compute_and( exclusive, values )
						exists_counter += 1
					except StringConditionsException:
						pass
				elif "|" in exclusive:
					try:
						compute_or( exclusive, values )
						exists_counter += 1
					except StringConditionsException:
						pass
				elif exclusive in values:
					exists_counter += 1

			if exists_counter > 1:
				raise StringConditionsException(
					"Only one of the following values are accepted: `{}`".format( c ) )
