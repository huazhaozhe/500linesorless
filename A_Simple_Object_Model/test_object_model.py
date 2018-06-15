# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time     : 2018/6/1 17:20
# @Author   : zhe
# @FileName : test_object_model.py
# @Project  : PyCharm

from .object_model import Class, Instance, TYPE, OBJECT

def test_read_write_field():

    class A:
        pass
    obj = A()
    obj.a = 1
    assert obj.a == 1
    obj.b = 5
    assert obj.a == 1
    assert obj.b == 5
    obj.a = 2
    assert obj.a == 2
    assert obj.b == 5

    A = Class(name='A', base_class=OBJECT, fields={}, metaclass=TYPE)
    obj = Instance(A)
    obj.write_attr('a', 1)
    assert obj.read_attr('a') == 1
    obj.write_attr('b', 5)
    assert obj.read_attr('a') == 1
    assert obj.read_attr('b') == 5
    obj.write_attr('a', 2)
    assert obj.read_attr('a') == 2
    assert obj.read_attr('b') == 5


def test_read_write_field_class():

    class A():
        pass
    A.a = 1
    assert A.a == 1
    A.a = 6
    assert A.a == 6

    A = Class(name='A', base_class=OBJECT, fields={'a': 1}, metaclass=TYPE)
    assert A.read_attr('a') == 1
    A.write_attr('a', 5)
    assert A.read_attr('a') == 5

def test_isinstance():

    class A():
        pass
    class B(A):
        pass
    b = B()
    assert isinstance(b, B)
    assert isinstance(b, A)
    assert isinstance(b, object)
    assert not isinstance(b, type)

    A = Class(name='A', base_class=OBJECT, fields={}, metaclass=TYPE)
    B = Class(name='B', base_class=A, fields={}, metaclass=TYPE)
    b = Instance(B)
    assert b.isinstance(B)
    assert b.isinstance(A)
    assert b.isinstance(OBJECT)
    assert not b.isinstance(TYPE)

def test_callmethod_simple():

    class A():
        def f(self):
            return self.x + 1
    obj = A()
    obj.x = 1
    assert obj.f() == 2

    class B(A):
        pass
    obj = B()
    obj.x = 1
    assert obj.f() == 2

    def f_A(self):
        return self.read_attr('x') + 1
    A = Class(name='A', base_class=OBJECT, fields={'f': f_A}, metaclass=TYPE)
    obj = Instance(A)
    obj.write_attr('x', 1)
    assert obj.read_attr('x') == 1
    assert obj.cls.read_attr('f')(obj) == 2
    assert obj.callmethod('f') == 2

    B = Class(name='B', base_class=A, fields={}, metaclass=TYPE)
    obj = Instance(B)
    obj.write_attr('x', 2)
    assert obj.cls.base_class.read_attr('f')(obj) == 3  # 与前面obj.cls.read_attr('f')(obj)相比较
    assert obj.callmethod('f') == 3

def test_callmethod_subclassing_and_arguments():
    class A():
        def g(self, arg):
            return self.x + arg
    obj = A()
    obj.x = 1
    assert obj.g(1) == 2

    class B(A):
        def g(self, arg):
            return self.x + arg * 2
    obj = B()
    obj.x = 4
    assert obj.g(3) == 10

    def g_A(self, arg):
        return self.read_attr('x') + arg
    A = Class(name='A', base_class=OBJECT, fields={'g': g_A}, metaclass=TYPE)
    obj = Instance(A)
    obj.write_attr('x', 1)
    assert obj.cls.read_attr('g')(obj, 4) == 5
    assert obj.callmethod('g', 4) == 5

    def g_B(self, arg):
        return self.read_attr('x') + arg * 2

    B = Class(name='B', base_class=A, fields={'g': g_B}, metaclass=TYPE)
    obj = Instance(B)
    obj.write_attr('x', 2)
    assert obj.cls.read_attr('g')(obj, 2) == 6
    assert obj.callmethod('g', 2) == 6

def test_bound_method():
    class A:
        def f(self, a):
            return self.x + a
    obj = A()
    obj.x = 2
    m = obj.f
    assert m(4) == 6

    class B(A):
        pass
    obj = B()
    obj.x = 1
    m = obj.f
    assert m(10) == 11

    def f_A(self, a):
        return self.read_attr('x') + a + 1
    A = Class(name='A', base_class=OBJECT, fields={'f': f_A}, metaclass=TYPE)
    obj = Instance(A)
    obj.write_attr('x', 2)
    m = obj.read_attr('f')
    assert m(4) == 7

    B = Class(name='B', base_class=A, fields={}, metaclass=TYPE)
    obj = Instance(B)
    obj.write_attr('x', 1)
    m = obj.read_attr('f')
    assert m(10) == 12
    assert obj.read_attr('f')(10) == 12

def test_getattr():
    class A:
        def __getattr__(self, name):
            if name == 'fahrenheit':
                return self.celsius * 9. / 5. + 32
            raise AttributeError(name)
        def __setattr__(self, name, value):
            if name == 'fahrenheit':
                self.celsius = (value - 32) * 5. / 9.
            else:
                object.__setattr__(self, name, value)
    obj = A()
    obj.celsius = 30
    assert obj.fahrenheit == 86
    obj.celsius = 40
    assert obj.fahrenheit == 104

    obj.fahrenheit = 86
    assert obj.celsius == 30
    assert obj.fahrenheit == 86

    def __getattr__(self, name):
        if name == 'fahrenheit':
            return self.read_attr('celsius') * 9. / 5. + 32
        raise AttributeError(name)
    def __setattr__(self, name, value):
        if name == 'fahrenheit':
            self.write_attr('celsius', (value - 32) * 5. / 9.)
        else:
            OBJECT.read_attr('__setattr__')(self, name, value)
    A = Class(name='A', base_class=OBJECT, fields={'__getattr__': __getattr__, '__setattr__': __setattr__}, metaclass=TYPE)
    obj = Instance(A)
    obj.write_attr('celsius', 30)
    assert obj.read_attr('fahrenheit') == 86
    obj.write_attr('celsius', 40)
    assert obj.read_attr('fahrenheit') == 104
    obj.write_attr('fahrenheit', 86)
    assert obj.read_attr('celsius') == 30
    assert obj.read_attr('fahrenheit') == 86

def test_get():
    class FahrenheitGetter():
        def __get__(self, inst, cls):
            return inst.celsius * 9. / 5. + 32

    class A():
        fahrenheit = FahrenheitGetter()

    obj = A()
    obj.celsius = 30
    assert obj.fahrenheit == 86

    class FahrenheitGetter():
        def __get__(self, inst, cls):
            return inst.read_attr('celsius') * 9. / 5. + 32

    A = Class(name='A', base_class=OBJECT, fields={'fahrenheit': FahrenheitGetter()}, metaclass=TYPE)
    obj = Instance(A)
    obj.write_attr('celsius', 30)
    assert obj.read_attr('fahrenheit') == 86

def test_maps():
    Point = Class(name='Point', base_class=OBJECT, fields={}, metaclass=TYPE)
    p1 = Instance(Point)
    p1.write_attr('x', 1)
    p1.write_attr('y', 2)
    assert p1.storage == [1, 2]
    assert p1.map.attrs == {'x': 0, 'y': 1}

    p2 = Instance(Point)
    p2.write_attr('x', 5)
    p2.write_attr('y', 6)
    assert p1.map is p2.map
    assert p2.storage == [5, 6]

    p1.write_attr('x', -1)
    p1.write_attr('y', -2)
    assert p1.map is p2.map
    assert p1.storage == [-1, -2]

    p3 = Instance(Point)
    p3.write_attr('x', 100)
    p3.write_attr('z', -343)
    assert p3.map is not p1.map
    assert p3.map.attrs == {'x': 0, 'z': 1}
