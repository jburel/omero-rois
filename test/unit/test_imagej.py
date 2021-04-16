#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 University of Dundee & Open Microscopy Environment.
# All rights reserved.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

from collections import OrderedDict
import pytest

from omero.model import PointI

from omero_rois import (
    convert_data,
)


@pytest.fixture
def shape_data():
    values = OrderedDict(
        [
            (
                "1",
                {
                    "type": "point",
                    "x": [0],
                    "y": [1],
                    "n": 1,
                    "name": "1",
                    "counters": [0],
                    "slices": [153],
                    "position": {"channel": 1, "slice": 2, "frame": 3},
                },
            ),
            (
                "2",
                {
                    "type": "point",
                    "x": [0],
                    "y": [1],
                    "n": 1,
                    "name": "2",
                    "position": 0,
                },
            ),
        ]
    )
    return values


class TestImageJUtils(object):
    def test_roi_from_shape_data(self, shape_data):
        assert shape_data is not None
        shapes = convert_data(shape_data)

        assert len(shapes) == 2
        for shape in shapes:
            if type(shape) == PointI:
                assert shape.getX().getValue() == 0
                assert shape.getY().getValue() == 1
