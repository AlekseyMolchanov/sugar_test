#!/usr/bin/env python
# encoding: utf-8


def inc(x):
    return x + 1


def test_one():
    assert inc(3) == 4
    
def test_second():
    assert inc(3) == 4