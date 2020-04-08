from fireservice.exceptions import ValidationError


def required():
    """Makes value as required.

    Raises:
        `ValidationError`
    """
    def _required(name, value):
        if value is None:
            raise ValidationError(name, 'Required field cannot be empty')
    return _required


def not_required():
    """Makes value as optional.
    """
    def _not_required(name, value):
        pass
    return _not_required


def length(*, min_length=None, max_length=None):
    """Checks value length using *__len__*
    
    Args:
        min_length (int, optional): If given, provided value's length should be greater than this.
        max_length (int, optional): If given, provided value's length should be less than this.
    
    Raises:
        `ValidationError`
    """
    def _length(name, value):
        length = len(value)
        if min_length is not None and length < min_length:
            raise ValidationError(name, 'Provided length: %s is less than min length: %s' % (length, min_length))
        if max_length is not None and length > max_length:
            raise ValidationError(name, 'Provided length: %s is greater than max length: %s' % (length, max_length))
    return _length


def interval(*, min_value=None, max_value=None):
    """Checks if value falls within a range.
    
    Args:
        min_value (int, optional): If given, provided value should be greater than this value.
        max_value (int, optional): If given, provided value should be less than this value.
    
    Raises:
        `ValidationError`
    """
    def _interval(name, value):
        if min_value is not None and value < min_value:
            raise ValidationError(name, 'Given value: %s is less than min: %s' % (value, min_value))
        if max_value is not None and value > max_value:
            raise ValidationError(name, 'Given value: %s is greater than max: %s' % (value, max_value))
    return _interval
