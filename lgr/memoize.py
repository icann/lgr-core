# -*- coding: utf-8 -*-
"""
memoize.py - Definition of memoize decorators.
"""
from __future__ import unicode_literals
import functools


class MethodAttributeMemoizer(object):
    """
    Define a decorator which caches results of an instance method.
    Results are cached according to the value of a specific instance attribute.
    """

    def __init__(self, attribute_name):
        """
        Create the decorator, by giving the instance attribute name.
        """
        # The decorator has arguments which are given to __init__ function
        self.attribute_name = attribute_name

    def __call__(self, func):
        # The function itself is only available here
        @functools.wraps(func)
        def wrapped_f(*args, **kwargs):
            # Retrieve concerned object
            obj = args[0]
            # Find/create the cache
            try:
                cache = obj.__cache
            except AttributeError:
                cache = obj.__cache = {}
            # Generate a key
            key = (str(func.__name__), str(getattr(obj, self.attribute_name)), str(args[1:]) + str(kwargs.items()))
            if key not in cache:
                cache[key] = func(*args, **kwargs)
            return cache[key]

        return wrapped_f
