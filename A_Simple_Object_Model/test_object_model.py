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
