"""
Module for a Django Field subclass for storing Frecency objects
in your database (with Float at the internal representation).

(https://docs.djangoproject.com/en/dev/howto/custom-model-fields/)

TODO: Add tests along these lines:
https://github.com/gintas/django-picklefield/blob/master/src/picklefield/tests.py


by Michael J.T. O'Kelly, 2014-04-09
"""

from django.db import models
import numpy

import frecency


DEFAULT_TIMESCALE = 24. * 60. * 60.


class FrecencyField(models.FloatField):

    description = "Field for storing Frecency objects"

    __metaclass__ = models.SubfieldBase

    def __init__(self, timescale=DEFAULT_TIMESCALE, *args, **kwargs):
            self.timescale = timescale
            # Allow None values by default, because we will interpret 
            # them as -Infinity (which is not supported by FloatField).
            kwargs.setdefault('null', True)
            kwargs.setdefault('blank', True)
            kwargs.setdefault('editable', False)
            super(FrecencyField, self).__init__(*args, **kwargs)

    def deconstruct(self):
            name, path, args, kwargs = super(FrecencyField, self).deconstruct()
            # Only include kwarg if it's not the default
            if self.timescale != DEFAULT_TIMESCALE:
                kwargs['timescale'] = self.timescale
            return name, path, args, kwargs

    def to_python(self, value):
        if isinstance(value, frecency.Frecency):
            return value
        elif isinstance(value, basestring):
            value = float(value)
        elif value is None:
            value = -numpy.Infinity

        # 'value' must be a float at this point
        f = frecency.Frecency(timescale=self.timescale)
        f.log2_value = value  # Overwrite the Frecency internal with the value from the database
        return f

    def get_prep_value(self, value):
        internal_value = value.log2_value
        return internal_value




