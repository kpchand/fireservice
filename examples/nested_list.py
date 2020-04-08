from fireservice import ListField, CharacterField, FireService


class Service(FireService):
    a = ListField(ListField(ListField(CharacterField())))

    def fire(self, **kwargs):
        print(self.a)


s = Service()
s.call({
    'a': [[['a', 'b'], ['c', 'd']], [['e', 'f'], ['g', 'h']]]
})
