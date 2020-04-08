class FireServiceError(Exception):
    """Base class for `FireService` errors.
    """


class SkipError(FireServiceError):
    """Raising this error skips the execution of `FireService`.
    """


class ValidationError(FireServiceError):
    """This exception contains input validation errors.
    """
    def __init__(self, field, error):
        """
        Args:
            field ([str]): The name of the field in `FireService` class.
            error ([str]): The error description.
        """
        super().__init__('Field "%s": %s' % (field, error))
        self.field = field
        self.error = error


class UnknownParameterError(FireServiceError):
    """This error is raised when input contains a key which doesn't match any declared fields in a `FireService` class.
    """


class ModificationError(FireServiceError):
    """This error is raised when a field value is tried to be modified.
    """

