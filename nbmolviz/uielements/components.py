# Copyright 2017 Autodesk Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from builtins import str
import ipywidgets as ipy
from ..widget_utils import process_widget_kwargs


class StyledTab(ipy.Tab):
    """
    Objects can inherit from this to maintain consistent styling.
    TODO: Probably better to do this with CSS?
    """

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('font_size', 9)
        super(StyledTab, self).__init__(*args, **process_widget_kwargs(kwargs))



class ReadOnlyRepr(ipy.Box):
    """ When a value is assigned, displays its __repr__ instead
    """
    def __init__(self, *args, **kwargs):
        super(ReadOnlyRepr, self).__init__(*args, **process_widget_kwargs(kwargs))
        self.textbox = ipy.Text()
        self.textbox.disabled = True
        self.children = [self.textbox]

    @property
    def value(self):
        return self.textbox.value

    @value.setter
    def value(self, v):
        self.textbox.value = repr(v)


class UnitText(ipy.Box):
    """Widget for a user to input a quantity with physical units.

    Args:
        value (u.Scalar): initial value for the widget
        units (u.MdtUnit): if provided, require that input has the same dimensionality as these
            units

    Note:
        A very rough approximation of the FloatText, IntText, etc. widgets - this does NOT have a
        counterpart in JavaScript. But it will behave similarly when setting units and values
        from python.

    """
    INVALID = u'\u274C'
    VALID = u"\u2705"

    def __init__(self, value=None, units=None, **kwargs):
        kwargs.setdefault('display', 'flex')
        kwargs.setdefault('flex_flow','row wrap')
        super(UnitText, self).__init__(layout=ipy.Layout(display='flex', flex_flow='row wrap'),
                                       **process_widget_kwargs(kwargs))
        self.textbox = ipy.Text()
        self.textbox.observe(self._validate, 'value')
        self._error_msg = None

        if units is not None:
            self.dimensionality = u.get_units(units).dimensionality
        else:
            self.dimensionality = None

        self._validated_value = None
        self.validated = ipy.HTML(self.INVALID)
        self.children = [self.textbox, self.validated]
        self._is_valid = False
        if value is not None:
            self.value = value

    def _validate(self, change):
        import pint

        self._validated_value = None
        self._error_msg = False

        # Check that we can parse this
        try:
            val = u.ureg(change['new'])

        except (pint.UndefinedUnitError,
                pint.DimensionalityError,
                pint.compat.tokenize.TokenError):
            self._error_msg = "Failed to parse '%s'" % self.textbox.value

        except Exception as e:  # unfortunately, pint's parser sometimes raises bare exception class
            if e.__class__ != Exception:
                raise  # this isn't what we want
            self._error_msg = "Failed to parse '%s'" % self.textbox.value

        else:  # Check dimensionality
            valdim = u.get_units(val).dimensionality
            if self.dimensionality is not None and valdim != self.dimensionality:
                self._error_msg = "Requires dimensionality %s" % self.dimensionality

        if not self._error_msg:
            self.validated.value = '<span title="Valid quantity">%s</span>' % self.VALID
            self._validated_value = val
        else:
            self.validated.value = '<span title="%s">%s</span>' % (self._error_msg, self.INVALID)

    @property
    def value(self):
        if self._validated_value is None:
            raise ValueError(self._error_msg)
        else:
            return self._validated_value

    @value.setter
    def value(self, v):
        self.textbox.value = str(v)
