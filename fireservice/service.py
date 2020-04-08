from fireservice.fields import Field
from fireservice.exceptions import ValidationError, UnknownParameterError, SkipError


class FireService:
    """The main class which manages the execution of services. Users should subclass this class to make their execution managed.
    
    ```
    class SendWelcomeEmail(FireService):
        name = StringField()
        email = EmailField()

        def pre_fire(self):
            if not connection_up():
                raise SkipError('Connection is down!')

        def fire(self):
            send_welcome_email(self.name, self.email, 'Hello %s, we are happy to see you back on Endurance!' % name)

        def post_fire(self, fired, exc):
            if fired:
                log_email_success(self.name, self.email)
            else:
                log_email_failure(self.name, self.email, exc)

    SendWelcomeEmail.call({
        'name': 'Murphy Cooper',
        'email': 'murphy@example.com'
    })
    ```

    Raises:
        UnknownParameterError: Raised when `call()` is called with a parameter with no corresponding declared `Field`.
        NotImplementedError: Raised when an abstract method is not implemented. The `fire()` method should be implemented all subclasses.
    """
    
    def call(self, input, **kwargs):
        """This method should be called from outside to start the execution of service.
        It performs input validations based on defined instances of `Field` and starts execution.
        
        Args:
            input (dict): Dictionary of input values corresponding to `Field` instances in `FireService` class.

        Use keyword arguments to pass some extra parameters to *fire()* method.
        
        Returns:
            object: Return value of `fire()` method.
        
        Raises:
            UnknownParameterError: Raised when `input` contains a key which doesn't match any declared `Field`.
            ValidationError: Raised when input validation based on definition of `Field` fails.
        """
        self._process_input(input)
        call_fire = True
        exc = None
        return_value = None
        try:
            self.pre_fire()
        except SkipError as ex:
            call_fire = False
            exc = ex
        if call_fire:
            return_value = self.fire(**kwargs)
        self.post_fire(call_fire, exc)
        return return_value

    def _process_input(self, input):
        fields = self._get_fields(type(self))
        field_names = [name for name, _ in fields]

        for key in input.keys():
            if key not in field_names:
                raise UnknownParameterError('Unknown parameter: %s provided' % key)

        for name, desc_obj in fields:
            input_value = input.get(name, Field.NULL)
            desc_obj._init_value(self, input_value)

    @staticmethod
    def _get_fields(subclass):
        return [(name, desc_obj) for name, desc_obj in subclass.__dict__.items() if isinstance(desc_obj, Field)]

    def pre_fire(self):
        """Method called before the execution of service, that is, called before the `fire()` method.
        Raise *SkipError()* here to prevent the execution of `fire()`.
 
        Raises:
            SkipError: Raising the exception skips the control flow to `post_fire()` method preventing the execution of `fire()` method.
            Usually used to prevent execution based on some conditions.
        """
        pass

    def fire(self, **kwargs):
        """The entry point of your service. This method should be implemented in your service. 
        
        Raises:
            NotImplementedError: Raised if user subclass does not implement this method.
        """
        raise NotImplementedError()

    def post_fire(self, fired, exc):
        """Called post `fire()` if that method was called and also called if `fire()` method execution was skipped in `pre_fire()`
        Mostly used to perform cleanup or logging operations post service execution.

        Note: This method is never called if their was an error other than `SkipError`.
        
        Args:
            fired (bool): Flag indication if `fire()` method was called.
            exc (SkipError): Contains exception raised in `pre_fire()` or `fire()` methods otherwise None.
        """
        pass
