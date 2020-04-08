from fireservice import StringField, FireService
from fireservice.exceptions import ValidationError


class IDField(StringField):
    """A `Field` which takes input in the pattern xxx-yyy-zzz.
    """
    def default_validator(self, value):
        # Use StringField validator to validate str
        super().default_validator(value)
        value = value.split('-')
        if len(value) != 3 or not all([len(v) == 3 for v in value]):
            raise ValidationError(self.name, 'Improper format')


class Service(FireService):
    user_id = IDField()

    def fire(self, **kwargs):
        print('user_id: ', self.user_id)


s = Service()
s.call({
    'user_id': 'foo-bar-baz'
    }
)
