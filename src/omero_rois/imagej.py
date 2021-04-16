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
from omero.model import EllipseI
from omero.model import LineI
from omero.model import PolylineI
from omero.model import PolygonI
from omero.model import PointI
from omero.model import RectangleI
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
    if type(position) is dict:
        z = position.get("slice") - 1
        c = position.get("channel") - 1
        t = position.get("frame") - 1
    return (z, c, t)


def format_shape(shape, value):
    """
    Extract the position, name etc. from the
    specified value and format the shape
    :param shape: The shape
    :param value: The dictionary to convert.
    """
    (z, c, t) = handle_position(value)
    if c >= 0:
        shape.theC = rint(c)
    if z >= 0:
        shape.theZ = rint(z)
    if t >= 0:
        shape.theT = rint(t)
    shape.textValue = rstring(value.get("name"))


def convert_as_point(value):
    """
    Convert the specified value into a Point
    :param value: The dictionary to convert.
    :return: A collection of OME points
    """
    shapes = []
    x_coordinates = value.get("x")
    y_coordinates = value.get("y")
    for i in range(len(x_coordinates)):
        point = PointI()
        point.x = rdouble(x_coordinates[i])
        point.y = rdouble(y_coordinates[i])
        format_shape(point, value)
        shapes.append(point)
    return shapes


def convert_as_rectangle(value):
    """
    Convert the specified value into a rectangle
    :param value: The dictionary to convert.
    :return: An OME rectangle
    """
    shape = RectangleI()
    shape.x = rdouble(value.get("left"))
    shape.y = rdouble(value.get("top"))
    shape.width = rdouble(value.get("width"))
    shape.height = rdouble(value.get("heigh"))
    format_shape(shape, value)
    return shape


def convert_as_line(value):
    """
    Convert the specified value into a line
    :param value: The dictionary to convert.
    :return: An OME line
    """
    shape = LineI()
    shape.x1 = rdouble(value.get("x1"))
    shape.y1 = rdouble(value.get("y1"))
    shape.x2 = rdouble(value.get("x2"))
    shape.y2 = rdouble(value.get("y2"))
    format_shape(shape, value)
    return shape


def convert_as_ellipse(value):
    """
    Convert the specified value into an Ellipse
    :param value: The dictionary to convert.
    :return: An OME ellipse
    """
    x = value.get("left")
    y = value.get("top")
    w = value.get("width") / 2
    h = value.get("heigh") / 2
    shape = EllipseI()
    shape.x = rdouble(x + w)
    shape.y = rdouble(y + h)
    shape.radiusX = rdouble(w)
    shape.radiusY = rdouble(h)
    format_shape(shape, value)
    return shape


def convert_as_polygon(value):
    """
    Convert the specified value into a Polygon
    :param value: The dictionary to convert.
    :return: An OME polygon
    """
    shape = PolygonI()
    x_list = value.get("x")
    y_list = value.get("y")
    points = ", ".join(["%s,%s" % (x, y) for x, y in zip(x_list, y_list)])
    shape.points = rstring(points)
    format_shape(shape, value)
    return shape


def convert_as_polyline(value):
    """
    Convert the specified value into a Polyline
    :param value: The dictionary to convert.
    :return: An OME polyline
    """
    shape = PolylineI()
    x_list = value.get("x")
    y_list = value.get("y")
    points = ", ".join(["%s,%s" % (x, y) for x, y in zip(x_list, y_list)])
    shape.points = rstring(points)
    format_shape(shape, value)
    return shape


def convert(value):
    """
    Convert the specified value into the shapes matching the ImageJ type.
    :param value: The dictionary to convert.
    :return: A collection of OME shapes
    """
    roi_type = value.get("type").lower()
    if roi_type == "point":
        return convert_as_point(value)
    elif roi_type == "rectangle":
        return convert_as_rectangle(value)
    elif roi_type == "line":
        return convert_as_line(value)
    elif roi_type == "oval":
        return convert_as_ellipse(value)
    elif roi_type == "polygon" or roi_type == "freehand" or roi_type == "traced":
        return convert_as_polygon(value)
    elif roi_type == "polyline" or roi_type == "angle" or roi_type == "freeline":
        return convert_as_polyline(value)
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
