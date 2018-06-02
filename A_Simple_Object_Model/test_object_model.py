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
