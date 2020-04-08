import re
import numbers
from datetime import date, datetime
from fireservice import validators 
from fireservice.exceptions import FireServiceError, ValidationError, ModificationError


class Field:
    """Base class for all `Field` types
    
    Raises:
        ModificationError: Raised when a `Field` value is modified. All field values are immutable and initialized during `FireService` instantination.
        ValidationError: Raised when `Field` value fails validation.
    
    """
    _MOD_FLAG_KEY = '_field_flags'

    NULL = object()
    """Special value to denote fields which have not been initialized.
    """

    def __init__(self, default=None, validators=[validators.required()], **options):
        """
        Args:
            default (object, optional): Instantinates `FireService` `Field` with this value. Defaults to None.
            validators (list, optional): A list of validators to apply. 
            Validators are functions with signature: `validator(name, value)` where `name` is attribute name of a `FireService` field and `value` is the provided value.
            Defaults to [validators.required()] which means that all fields are required by default.
            Explicitly set this option as [validators.not_required()] to make this field optional.
        """
        self.options = {}
        """The keyword arguments provided to `Field`.
        """
        self.name = None
        """The name of the `FireService` attribute to which this `Field` is assigned.
        """
        self.options['default'] = default
        self.options['validators'] = validators
        self.options.update(**options)

    def __set_name__(self, owner, name):
        self.name = name
        """Name of the attribute in a `FireService` class
        """

    def __get__(self, instance, instance_type):
        return instance.__dict__.get(self.name)

    def __set__(self, instance, value):
        mod_dict = instance.__dict__.get(self._MOD_FLAG_KEY)
        if mod_dict and mod_dict.get(self.name):
            raise ModificationError('Attempt to change field: %s' % self.name)
        instance.__dict__[self.name] = value
        if not mod_dict:
            instance.__dict__[self._MOD_FLAG_KEY] = {}
        instance.__dict__[self._MOD_FLAG_KEY][self.name] = True

    def _init_value(self, instance, input_value):
        if input_value == self.NULL:
            value = self.options['default']
        else:
            value = input_value
        self._run_validation(value)
        setattr(instance, self.name, value)

    def _run_validation(self, value):
        for validator in self.options['validators']:
            validator(self.name, value)
        if value is None:
            return
        self.default_validator(value)

    def default_validator(self, value):
        """The default validator for a `Field` type which will always be applied after all user supplied validators.

        Args:
            value (object): The provided value when starting the service.

        Raises:
            ValidationError: Raised when validation failed.
        """
        pass


class BooleanField(Field):
    """Field which takes a boolean type.
    """
    def __init__(self, **options):
        super().__init__(**options)

    def default_validator(self, value):
        if not isinstance(value, bool):
            raise ValidationError(self.name, 'Not of bool type')


class CharacterField(Field):
    """Field which takes a character type which is a string of maximum length: 1
    """
    def __init__(self, **options):
        super().__init__(**options)

    def default_validator(self, value):
        if not isinstance(value, str):
            raise ValidationError(self.name, 'Not of str type')
        length = len(value)
        if length == 0 or length > 1:
            raise ValidationError(self.name, 'Should have length: 1 but has length: %s' % length)


class StringField(Field):
    """`Field` which takes a `str` type.
    """
    def __init__(self, min_length=None, max_length=None, **options):
        """
        Args:
            min_length (int, optional): The minimum length of string. Defaults to unbounded.
            max_length ([type], optional): The maximum length of string. Defaults to unbounded.
        """
        super().__init__(min_length=min_length, max_length=max_length, **options)

    def default_validator(self, value):
        if not isinstance(value, str):
            raise ValidationError(self.name, 'Not of str type')
        validator = validators.length(min_length=self.options.get('min_length'), max_length=self.options.get('max_length'))
        validator(self.name, value)


class NumericField(Field):
    """`Field` which takes a `numeric` type.
    """
    def __init__(self, min_value=None, max_value=None, **options):
        """
        Args:
            min_value (int, optional): If given, the provided value should be greater than this.
            max_value (int], optional): If given, the provided value should be less than this.
        """
        super().__init__(min_value=min_value, max_value=max_value, **options)

    def default_validator(self, value):
        if not isinstance(value, numbers.Number):
            raise ValidationError(self.name, 'Not of numeric type')
        validator = validators.interval(min_value=self.options.get('min_value'), max_value=self.options.get('max_value'))
        validator(self.name, value)


class IntegerField(NumericField):
    """Field which takes an `int` type.
    """
    def default_validator(self, value):
        super().default_validator(value)
        if not isinstance(value, int):
            raise ValidationError(self.name, 'Not of int type')


class FloatField(NumericField):
    """Field which takes a `float` type.
    """
    def default_validator(self, value):
        super().default_validator(value)
        if not isinstance(value, float):
            raise ValidationError(self.name, 'Not of float type')


class DateField(Field):
    """Field which takes a `date` type
    """
    def default_validator(self, value):
        if isinstance(value, datetime) or not isinstance(value, date):
            raise ValidationError(self.name, 'Not of date type')


class DateTimeField(Field):
    """Field which takes a `datetime` type.
    """
    def __init__(self, **options):
        super().__init__(**options)

    def default_validator(self, value):
        if not isinstance(value, datetime):
            raise ValidationError(self.name, 'Not of datetime type')


class DictField(Field):
    """Field which takes a `dict` type
    """
    def __init__(self, **options):
        super().__init__(**options)

    def default_validator(self, value):
        if not isinstance(value, dict):
            raise ValidationError(self.name, 'Not of dict type')


class EmailField(Field):
    """Field which takes an email `str`.
    What constitutes an email is very lax and it only checks for presence of '@' and domain.
    There is no fool-proof way to confirm a valid email unless an email is sent at that address.
    """
    def __init__(self, **options):
        super().__init__(**options)

    def default_validator(self, value):
        if not isinstance(value, str):
            raise ValidationError(self.name, 'Not of str type')
        error = False
        try:
            if not re.fullmatch(r'[^@]+@[^@]+\.[^@]+', value):
                error = True
        except TypeError:
            error = True
        if error:
            raise ValidationError(self.name, 'Not a valid email')


class ListField(Field):
    """Field which takes a collection of other Fields.
    """
    def __init__(self, item, is_root=True, min_length=None, max_length=None, **options):
        """It allows theoretically infinite number of nested fields. For example:

            ListField(ListField(ListField(CharacterField())))
            
            for an input value:

            [[['a', 'b'], ['c', 'd']], [['e'], ['f', 'g']]]

        Valid input values should either be of `list` or `tuple` type.

        Args:
            item (Field): An instance of a `Field` which this `list` will hold.
            is_root (bool, optional): This value should not be tampered with unless you exactly know what you are doing.
            min_length (int, optional): If given, the length of the provided `list` should be greater than this.
            max_length (int, optional): If given, the length of the provided `list` should be less than this.
        
        Raises:
            FireServiceError: Raised when `item` is not of `Field` type.
        """
        if not isinstance(item, Field):
            raise FireServiceError('ListField needs a Field type as contained item type')
        super().__init__(min_length=min_length, max_length=max_length, **options)
        self.item = item
        self.is_root = is_root

    def _init_value(self, instance, input_value):
        if input_value == Field.NULL:
            input_value = self.options['default']

        internal_name = '_' + str(id(instance)) + '_' + self.name
        self._run_validation(input_value)
        set_value = None
        if input_value is not None:
            set_value = []
            for i, v in enumerate(input_value):
                if isinstance(self.item, ListField):
                    self._init_item_field(i, internal_name, v, self.item.item, is_root=False, **self.item.options)
                else:
                    self._init_item_field(i, internal_name, v, **self.item.options)
                set_value.append(self.__dict__[internal_name])
                del self.__dict__[internal_name]

        setattr(instance, self.name, set_value)

    @staticmethod
    def _is_valid_type(value):
        if isinstance(value, list) or isinstance(value, tuple) or isinstance(value, ListField):
            return True
        return False

    def _init_item_field(self, idx, name, value, *args, **kwargs):
        f = type(self.item)(*args, **kwargs)
        f.__set_name__(self, name)
        try:
            f._init_value(self, value)
        except ValidationError as ex:
            field = '' if ex.field.startswith('_') else ex.field
            if not self.is_root:
                raise ValidationError('[%s]%s' % (idx, field), ex.error)
            field = '%s[%s]%s' % (self.name, idx, field)
            raise ValidationError(field, ex.error)

    def default_validator(self, value):
        valid_type = isinstance(value, list) or isinstance(value, tuple)
        if not valid_type:
            raise ValidationError(self.name, 'Not of list or tuple type')
        validator = validators.length(min_length=self.options.get('min_length'), max_length=self.options.get('max_length'))
        validator(self.name, value)
