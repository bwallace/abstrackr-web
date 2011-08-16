import formencode
from formencode import validators
from pylons.decorators import validate
import abstrackr.model as model

class UniqueUsername(formencode.FancyValidator):
    def _to_python(self, value, state):
        user_q = model.meta.Session.query(model.User)
        usernames = [user.username for user in user_q.all()]
        if value in usernames:
            raise formencode.Invalid(
                    'Sorry, that username already exists. Try something else.',
                     value, state)
            return value
            
class RegisterForm(formencode.Schema):
    allow_extra_fields = True
    filter_extra_fields = True
    email = formencode.validators.Email(not_empty=True)
    first_name = formencode.validators.String(not_empty=True)
    last_name =  formencode.validators.String(not_empty=True)
    experience = formencode.validators.Int(not_empty=True)
    password = formencode.validators.NotEmpty()
    username = UniqueUsername()
    

    
class ChangePasswordForm(formencode.Schema):
    allow_extra_fields = True
    chained_validators = [validators.FieldsMatch(
                         'password', 'password_confirm')]


