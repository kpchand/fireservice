# FireService

FireService is a simple library to create Python Services.

* Declarative input fields.
* Input validations.
* Immutable fields.
* Execution callbacks.
* Less biolerplate.
* Works with native Python objects wherever possible.
* Extensible with custom field types and validators.
* Provides an elegant superstructure for classes which work on any input.

## Installation

To install FireService using pip, run: ```pip install fireservice```

To install FireService using pipenv, run: ```pipenv install fireservice```


## Basic Usage

```python
from fireservice import IntegerField, StringField, FireService
from fireservice.exceptions import SkipError, ValidationError


CRAWLED_DB = []

def page_name_validator(name, value):
    if not value.endswith('.html'):
        raise ValidationError(name, 'I only know html pages!')


class Crawler(FireService):
    # All fields are required by default
    user_id = IntegerField(min_value=1)
    page_name = StringField(validators=[page_name_validator])

    def url(self):
        # Fields are directly accessible using instance __dict__
        return 'http://example.com/{}/{}'.format(self.user_id, self.page_name)

    def pre_fire(self):
        if self.url() in CRAWLED_DB:
            # Control directly goes to post_fire method
            raise SkipError('Page already crawled!')
    
    def fire(self, **kwargs):
        CRAWLED_DB.append(self.url())

    def post_fire(self, fired, exc):
        if fired:
            print('I crawled!')
        else:
            print('I skipped crawling because: ', exc)


crawler = Crawler()
crawler.call({
    'user_id': 1,
    'page_name': 'about.html'
})

# Values are stored in native python types wherever possible:
print(type(crawler.user_id), type(crawler.page_name))  # <class 'int'> <class 'str'>

# Raises ModificationError as all Fields are immutable
crawler.user_id = 2 
```

A slightly convoluted example to show nested field types:

```python
class Service(FireService):
    a = ListField(ListField(ListField(CharacterField())))

    def fire(self, **kwargs):
        print(self.a)


s = Service()
s.call({
    'a': [[['a', 'b'], ['c', 'd']], [['e', 'f'], ['g', 'h']]]
})

```


## What is a Service?

Services are a part of the domain model which performs some business logic. Usually they work on a set of inputs and change some state or return a computed value. In languages like Python which are not type safe, input validation and a common interface for programs which work on dynamic inputs could be an issue.

Some reading resources :
* https://en.wikipedia.org/wiki/Service_layer_pattern
* https://www.martinfowler.com/bliki/AnemicDomainModel.html


## Docs

View the Docs at: https://kpchand.github.io/fireservice/.
If redirection fails, then directly go [here](https://kpchand.github.io/fireservice/fireservice/index.html).


## Extending FireService

We can also create custom fields. Suppose our application takes user ID with the pattern *xxx-yyy-zzz*. We can create a `StringField ` and use a custom *validator*. But it would be more convenient & declarative if we had a `Field` type which did this validation by default. Here is an example of such an implementation:


```python
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
```


## Inspiration

FireService was inspired from [django-service-objects](https://github.com/mixxorz/django-service-objects) but designed to work with any framework and as close to raw Python as possible. 


## Why is it called FireService

When you invoke `call()` it starts `fire()` which in turn starts the `FireService`.
