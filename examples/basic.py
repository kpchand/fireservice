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