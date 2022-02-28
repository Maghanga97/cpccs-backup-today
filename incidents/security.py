import hashlib
from .models import CountyUsers

""" the hash function was changed so remember to apply the necessay changes to all the parts of the code 
the reference/call it """
def hash_password(salt, password):
    return hashlib.sha384((salt.encode() + password.encode())).hexdigest()

def hash_phrase(phrase):
	return hashlib.sha384(phrase.encode()).hexdigest()


SESSION_KEY='dff6cad193a6ca7720c35baad437cfedff2a13883fe04518c6fcdbfc1e1055ee7f3845d3974dec1a7c8f10cc627918be'

def authenticated(username, password):
	try:
		user_object= CountyUsers.objects.get(user_name=username)
		authenticate_username=user_object.user_name
		authenticate_password=user_object.user_pass
		#the expression below was changed-the argument passed was changed
		produce_hash=hash_password(authenticate_username, password)
		if authenticate_password == produce_hash:
			return True
		else:
			return f"The password you entered does not match the login"
	except Exception as e:
		return f"User does not exist"





