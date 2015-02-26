class Descriptor(object):

    def __init__(self):
        self._name = ''

    def __get__(self, instance, owner):
        print "Getting: %s" % self._name
        print instance
        print owner
        return self._name

    def __set__(self, instance, name):
        print "Setting: %s" % name
        self._name = name.title()

    def __delete__(self, instance):
        print "Deleting: %s" %self._name
        del self._name

class Person(object):
    name = Descriptor()

test = Descriptor()
print test

user = Person()
user.name = 'Walter'
print user.name