import pytest
from datetime import datetime, date
from fireservice.validators import *
from fireservice.fields import *
from fireservice.exceptions import ValidationError


def init_field_holder(field):
    class FieldHolder:
        a = field

    return FieldHolder()


@pytest.mark.parametrize('field, value', [
    (BooleanField(), 1),
    (CharacterField(), 1),
    (StringField(), 1),
    (NumericField(), 'a'),
    (IntegerField(), 1.5),
    (FloatField(), 1),
    (DateField(), datetime.now()),
    (DateTimeField(), datetime.now().date()),
    (DictField(), []),
    (EmailField(), 'aaa.com'),
    (ListField(StringField()), {})
])
def test_invalid_value_type_raises_error(field, value):
    # Given: required is True
    fh = init_field_holder(field)

    # When: init with invalid value type
    # Then: raise error
    with pytest.raises(ValidationError):
        field._init_value(fh, value)


@pytest.mark.parametrize('field', [
    BooleanField(validators=[required()]),
    CharacterField(validators=[required()]),
    StringField(validators=[required()]),
    NumericField(validators=[required()]),
    IntegerField(validators=[required()]),
    FloatField(validators=[required()]),
    DateField(validators=[required()]),
    DateTimeField(validators=[required()]),
    DictField(validators=[required()]),
    EmailField(validators=[required()]),
    ListField(StringField(validators=[required()]), validators=[required()])
])
def test_required_field_empty_raises_error(field):
    # Given: required is True
    fh = init_field_holder(field)

    # When: init with empty value
    # Then: raise error for empty value
    with pytest.raises(ValidationError):
        field._init_value(fh, Field.NULL)


@pytest.mark.parametrize('field, value', [
    (BooleanField(), True),
    (CharacterField(), 'a'),
    (StringField(), 'aaa'),
    (NumericField(), 1),
    (NumericField(), 1.0),
    (IntegerField(), 1),
    (FloatField(), 1.5),
    (DateField(), datetime.now().date()),
    (DateTimeField(), datetime.now()),
    (DictField(), {}),
    (EmailField(), 'aaa@aaa.com'),
    (ListField(StringField()), ['aaa'])
])
def test_returns_valid_value(field, value):
    # Given: required is True
    fh = init_field_holder(field)

    # When: init with boolean value type
    # Then: return value
    field._init_value(fh, value)
    assert field.__get__(fh, type(fh)) == value


@pytest.mark.parametrize('field', [
    BooleanField(default=True),
    CharacterField(default='a'),
    StringField(default='aaa'),
    NumericField(default=1.0),
    IntegerField(default=1),
    FloatField(default=1.5),
    DateField(default=datetime.now().date()),
    DateTimeField(default=datetime.now()),
    DictField(default={}),
    EmailField(default='aaa@aaa.com'),
    ListField(StringField(), default=['aaa'])
])
def test_returns_default_value(field):
    # Given: required is True and default is provided
    fh = init_field_holder(field)

    # When: init with no value
    # Then: return default value
    field._init_value(fh, Field.NULL)
    assert field.__get__(fh, type(fh)) == field.options['default']


@pytest.mark.parametrize('field', [
    BooleanField(validators=[not_required()]),
    CharacterField(validators=[not_required()]),
    StringField(validators=[not_required()]),
    NumericField(validators=[not_required()]),
    IntegerField(validators=[not_required()]),
    FloatField(validators=[not_required()]),
    DateField(validators=[not_required()]),
    DateTimeField(validators=[not_required()]),
    DictField(validators=[not_required()]),
    EmailField(validators=[not_required()]),
    ListField(StringField(validators=[not_required()]), validators=[not_required()])
])
def test_returns_none_when_not_required(field):
    # Given: required is False
    fh = init_field_holder(field)
    # When: init with no value
    # Then: return None
    field._init_value(fh, Field.NULL)
    assert field.__get__(fh, type(fh)) is None


@pytest.mark.parametrize('field, value', [
    (NumericField(validators=[interval(min_value=0)]), -1),
    (IntegerField(validators=[interval(min_value=0)]), -1),
    (FloatField(validators=[interval(min_value=2.0)]), 1.0)
])
def test_min_value_violation_raises_error(field, value):
    # Given: min option
    fh = init_field_holder(field)

    # When: init value less than min
    # Then: raise error
    with pytest.raises(ValidationError):
        field._init_value(fh, value)


@pytest.mark.parametrize('field, value', [
    (NumericField(validators=[interval(max_value=1)]), 2),
    (IntegerField(validators=[interval(max_value=1)]), 2),
    (FloatField(validators=[interval(max_value=1.0)]), 2.0)
])
def test_max_value_violation_raises_error(field, value):
    # Given: max option
    fh = init_field_holder(field)

    # When: init value greater than max
    # Then: raise error
    with pytest.raises(ValidationError):
        field._init_value(fh, value)


@pytest.mark.parametrize('field, value', [
    (StringField(validators=[length(min_length=2)]), 'a'),
    (ListField(IntegerField(), validators=[length(min_length=2)]), [1])
])
def test_min_length_violation_raises_error(field, value):
    # Given: min_length option
    fh = init_field_holder(field)

    # When: init len(value) less than min_length
    # Then: raise error
    with pytest.raises(ValidationError):
        field._init_value(fh, value)


@pytest.mark.parametrize('field, value', [
    (StringField(validators=[length(max_length=2)]), 'aaa'),
    (ListField(IntegerField(), validators=[length(max_length=2)]), [1, 2, 3])
])
def test_max_length_violation_raises_error(field, value):    
    # Given: max_length option
    fh = init_field_holder(field)

    # When: init len(value) less than max_length
    # Then: raise error
    with pytest.raises(ValidationError):
        field._init_value(fh, value)


@pytest.mark.parametrize('field, value', [
    (BooleanField(), True),
    (CharacterField(), 'a'),
    (StringField(), 'aaa'),
    (NumericField(), 1),
    (NumericField(), 1.0),
    (IntegerField(), 1),
    (FloatField(), 1.5),
    (DateField(), datetime.now().date()),
    (DateTimeField(), datetime.now()),
    (DictField(), {}),
    (EmailField(), 'aaa@aaa.com'),
    (ListField(StringField()), ['aaa'])
])
def test_modification_error_when_assigned_value_again(field, value):
    # Given: a Field and value
    fh = init_field_holder(field)
    field._init_value(fh, value)

    # When: assign value again
    # Then: raise error
    with pytest.raises(ModificationError):
        field._init_value(fh, value)
