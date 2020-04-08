import pytest
from functools import wraps
from fireservice.service import FireService
from fireservice.fields import IntegerField
from fireservice.exceptions import *


class RecordExec:
    def record(self, func):
        @wraps(func)
        def _record(obj, *args, **kwargs):
            value = {'_args': args, **kwargs}
            setattr(self, func.__name__, value)
            return func(obj, *args, **kwargs)
        return _record
    
    def __getattr__(self, name):
        return self.__dict__.get(name)


def test_validation_error():
    recorder = RecordExec()
    class Service(FireService):
        a = IntegerField(min_value=1)

        @recorder.record
        def pre_fire(self):
            pass

        @recorder.record
        def fire(self, **kwargs):
            pass

        @recorder.record
        def post_fire(self, fired, exc):
            pass
    
    s = Service()
    with pytest.raises(ValidationError):
        s.call({
            'a': 0
        })
    assert recorder.pre_fire is None
    assert recorder.fire is None
    assert recorder.post_fire is None


def test_unknown_parameter_error():
    recorder = RecordExec()
    class Service(FireService):
        a = IntegerField(min_value=1)

        @recorder.record
        def pre_fire(self):
            pass

        @recorder.record
        def fire(self, **kwargs):
            pass

        @recorder.record
        def post_fire(self, fired, exc):
            pass
    
    s = Service()
    with pytest.raises(UnknownParameterError):
        s.call({
            'b': 0
        })
    assert recorder.pre_fire is None
    assert recorder.fire is None
    assert recorder.post_fire is None


def test_skip_error():
    recorder = RecordExec()
    class Service(FireService):
        a = IntegerField(min_value=1)

        @recorder.record
        def pre_fire(self):
            raise SkipError()

        @recorder.record
        def fire(self, **kwargs):
            pass

        @recorder.record
        def post_fire(self, fired, exc):
            pass
    
    s = Service()
    s.call({
        'a': 10
    })
    assert recorder.pre_fire is not None
    assert recorder.fire is None
    assert recorder.post_fire is not None
    args = recorder.post_fire['_args']
    assert args[0] is False
    assert isinstance(args[1], SkipError)


def test_successful_execution():
    recorder = RecordExec()
    class Service(FireService):
        a = IntegerField(min_value=1)

        @recorder.record
        def pre_fire(self):
            pass

        @recorder.record
        def fire(self, **kwargs):
            pass

        @recorder.record
        def post_fire(self, fired, exc):
            pass
    
    s = Service()
    s.call({
        'a': 10
    })

    assert recorder.pre_fire is not None
    assert recorder.fire is not None
    assert recorder.post_fire is not None
    args = recorder.post_fire['_args']
    assert args[0] is True
    assert args[1] is None


def test_multiple_service_instances_have_different_field_values():
    # Given a service
    class Service(FireService):
        a = IntegerField(min_value=1)

        def pre_fire(self):
            pass

        def fire(self, **kwargs):
            pass

        def post_fire(self, fired, exc):
            pass

    # When creating different service instants with different values
    s1 = Service()
    s2 = Service()
    s1.call({
        'a': 10
    })
    s2.call({
        'a': 20
    })

    # Then: each service instant should store its own value
    assert s1.a == 10
    assert s2.a == 20