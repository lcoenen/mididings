# -*- coding: utf-8 -*-
#
# midipatch
#
# Copyright (C) 2007  Dominic Sacré  <dominic.sacre@gmx.de>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#

import _midipatch
import misc as _misc
from units import _Chain, _Unit
from units import *


class Patch(_midipatch.Patch):
    def __init__(self, p):
        _midipatch.Patch.__init__(self)

        i = Patch.Module(Patch.Input())
        o = Patch.Module(Patch.Output())

        r = self.build(p)

        # attach all inputs
        for c in r[0]:
            i.attach(c)
        # attach all outputs
        for c in r[1]:
            c.attach(o)

        self.set_start(i)

    # recursively connects all units in p
    # returns the lists of inputs and outputs of p
    def build(self, p):
        if isinstance(p, _Chain):
            # build both items
            a = self.build(p.items[0])
            b = self.build(p.items[1])
            # connect all of a's outputs to all of b's inputs
            for x in a[1]:
                for y in b[0]:
                    x.attach(y)
            # return a's inputs and b's outputs
            return a[0], b[1]
        elif isinstance(p, list):
            # build all items, return all inputs and outputs
            inp, outp = [], []
            for m in p:
                r = self.build(m)
                inp += r[0]
                outp += r[1]
            return inp, outp
        elif isinstance(p, _Unit):
            # single unit is both input and output
            m = Patch.Module(p)
            return [m], [m]
        else:
            # whoops...
            raise TypeError()


class Setup(_midipatch.Setup):
    def __init__(self, patches, control, preprocess, postprocess, default_patch,
                 backend, client_name, in_ports, out_ports, debug):
        in_portnames = _midipatch.string_vector()
        out_portnames = _midipatch.string_vector()

        if _misc.is_sequence(in_ports):
            # fill vector with input port names
            for i in in_ports:
                in_portnames.push_back(i)
            in_ports = len(in_ports)

        if _misc.is_sequence(out_ports):
            # fill vector with output port names
            for i in out_ports:
                out_portnames.push_back(i)
            out_ports = len(out_ports)

        _midipatch.Setup.__init__(self, backend, client_name,
                                  in_ports, out_ports, in_portnames, out_portnames, debug)

        for i, p in patches.items():
            if isinstance(p, tuple):
                init_patch, patch = Patch(p[0]), Patch(p[1])
            else:
                init_patch, patch = None, Patch(p)
            self.add_patch(i, patch, init_patch)

        ctrl = Patch(control) if control else None
        pre = Patch(preprocess) if preprocess else None
        post = Patch(postprocess) if postprocess else None
        self.set_processing(ctrl, pre, post)

        if default_patch != None:
            self.switch_patch(default_patch)


def run(patches, control=None, preprocess=None, postprocess=None,
        default_patch=None, backend='alsa', client_name='midipatch',
        in_ports=1, out_ports=1, debug=False):
    s = Setup(patches, control, preprocess, postprocess, default_patch,
              backend, client_name, in_ports, out_ports, debug)
    try:
        s.run()
    except KeyboardInterrupt:
        return


def test_run(patch, event):
    s = Setup({0: patch}, None, None, None, 0,
              'dummy', 'midipatch_test', 1, 1, False)
    r = s.process(event)
    return r[:]
