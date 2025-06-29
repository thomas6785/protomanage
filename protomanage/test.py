"""
Use a metaclass to enforce:
- Class metadata should be set explicitly and not inherited
- Class constructor should call base class constructor
- Abstract methods should be defined (ABCMeta will do this)
- from_dict(to_dict) should always return the same data
"""

from abc import ABC,abstractmethod,ABCMeta

def new_str_obj(s):
    return ''.join(s)  # Create a new string object with the same value (id will differ)

class MyMetaClass(ABCMeta):
    pass

class Base(metaclass=MyMetaClass):
    DISPLAY_NAME = ''.join("Base class")

    def __init__(self,a,b):
        print("Base init")
        self.a = a
        self.b = b

    @abstractmethod
    def test_method():
        """children should implement this"""
        pass

class Child(Base):
    DISPLAY_NAME = "Base class"

    def __init_subclass__(cls):
        print("Hello "+cls.__name__)

    def __init__(self,a,b):
        print("Child init")
        self.a = a
        self.b = b

class GrandChild(Child):
    def __init__(self,a,b):
        print("GrandChild init")
        self.a = a
        self.b = b

a = GrandChild(1,2)
b = Child(1,2)