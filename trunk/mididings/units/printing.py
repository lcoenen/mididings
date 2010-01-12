# -*- coding: utf-8 -*-
#
# mididings
#
# Copyright (C) 2008-2010  Dominic Sacré  <dominic.sacre@gmx.de>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#

from mididings.units.call import _CallBase
from mididings.units.base import _unit_repr

import mididings.constants as _constants
import mididings.misc as _misc
from mididings.misc import NamedFlag as _NamedFlag


class _Print(_CallBase):
    max_name_length = -1
    max_portname_length = -1
    portnames_used = False

    def __init__(self, name, types, portnames):
        self.name = name
        self.types = types
        self.portnames = portnames

        # to be calculated later
        self.ports = None

        if portnames != None:
            _Print.portnames_used = True

        # find maximum name length
        if name:
            _Print.max_name_length = max(_Print.max_name_length, len(name))

        _CallBase.__init__(self, self.do_print, True, True)

    def do_print(self, ev):
        # lazy import to avoid problems with circular imports
        from mididings import engine

        # get list of port names to be used
        # (delayed 'til first use, because the engine doesn't yet exist during __init__)
        if self.ports == None:
            if self.portnames == 'in':
                self.ports = engine.get_in_ports()
            elif self.portnames == 'out':
                self.ports = engine.get_out_ports()
            else:
                self.ports = []

        # find maximum port name length (delayed for the same reason as above)
        if _Print.portnames_used and _Print.max_portname_length == -1:
            all_ports = engine.get_in_ports() + engine.get_out_ports()
            _Print.max_portname_length = max(len(p) for p in all_ports)

        if ev.type & self.types:
            if self.name:
                print '%-*s' % (_Print.max_name_length + 1, self.name + ':'),
            elif _Print.max_name_length != -1:
                # no name, but names used elsewhere, so indent appropriately
                print ' ' * (_Print.max_name_length + 1),

            print ev.to_string(self.ports, _Print.max_portname_length)


class _PrintString(_CallBase):
    def __init__(self, string):
        self.string = string
        _CallBase.__init__(self, self.do_print, True, True)
    def do_print(self, ev):
        print self.string


@_unit_repr
@_misc.overload
def Print(name=None, types=_constants.ANY, portnames=None):
    return _Print(name, types, portnames)

@_unit_repr
@_misc.overload
def Print(string):
    return _PrintString(string)


# for backward compatibility
Print.PORTNAMES_NONE = None
Print.PORTNAMES_IN = 'in'
Print.PORTNAMES_OUT = 'out'


@_misc.deprecated('Print')
def PrintString(string):
    return Print(string=string)
