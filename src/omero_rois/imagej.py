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

from read_roi import read_roi_zip
from read_roi import read_roi_file
from omero.model import PointI
from omero.rtypes import (
    rdouble,
    rint,
    rstring,
)


def handle_position(value):
    """
    Determine the channel, z-section and timepoint
    """
    z = -1
    c = -1
    t = 0
    position = value.get("position")
    # TODO check dimension
    if (type(position) is dict):
        z = position.get("slice") - 1
        c = position.get("channel") - 1
        t = position.get("frame") - 1
    return (z, c, t)


def convert_as_point(value):
    """
    Convert the specified value into a Point
    :param value: The dictionary to convert.
    :return: A collection of OME points
    """
    shapes = []
    x_coordinates = value.get("x")
    y_coordinates = value.get("y")
    (z, c, t) = handle_position(value)
    name = value.get("name")
    slices = value.get("slices")
    for i in range(len(x_coordinates)):
        point = PointI()
        point.x = rdouble(x_coordinates[i])
        point.y = rdouble(y_coordinates[i])
        point.theZ = rint(z)
        point.theT = rint(t)
        point.textValue = rstring(name)
        shapes.append(point)
    return shapes


def convert(value):
    """
    Convert the specified value into the shapes matching the ImageJ type.
    :param value: The dictionary to convert.
    :return: A collection of OME shapes
    """
    roi_type = value.get("type").lower()
    if roi_type == "point":
        return convert_as_point(value)
    else:
        return None


def convert_data(values):
    """
    Convert the ImageJ Roi into the corresponding OME shapes.
    :param values: The file to handle.
    :return: A collection of OME shape objects
    """
    shapes = []
    for key, value in values.items():
        roi = convert(value)
        if roi is not None:
            shapes.extend(roi)
    return shapes
    

def read_roi(roi_file):
    """
    Read the Image ROI either from a zip or .roi file

    :param roi_file: The file to handle.
    :return: A collection of OME ROI objects
    :raises ValueError: If file specified is not supported
    """
    if roi_file.endswith(".zip"):
        values = read_roi_zip(roi_file)
    elif roi_file.endswith(".roi"):
        values = read_roi_file(roi_file)
    else:
        raise ValueError("File extension not supported.")
    return convert_data(values)
