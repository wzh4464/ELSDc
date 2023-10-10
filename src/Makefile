#
#  Copyright (c) 2012 viorica patraucean (vpatrauc@gmail.com)
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as
#  published by the Free Software Foundation, either version 3 of the
#  License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#  GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with this program. If not, see <http://www.gnu.org/licenses/>.
#
#  makefile - This file belongs to ELSDc project (Ellipse and Line Segment
#             Detector with continuous validation).

# You may need to indicate the location of Lapack library in your system.
# For that, uncomment the following line and replace `/usr/lib` with
# the directory where the library is located.

# if comupter name is mercury, use the following line
ifeq ($(shell hostname),mercury)
LIB= -L/home/zihan/lib
endif
OPT= -O3

elsdc: main.c pgm.c svg.c elsdc.c gauss.c curve_grow.c polygon.c ring.c ellipse_fit.c rectangle.c iterator.c image.c lapack_wrapper.c misc.c
	ifeq ($(shell hostname),mercury)
	cc $(OPT) $(LIB) -o $@ $^ -llapack -lm -lblas -lgfortran
	else
	cc $(OPT) $(LIB) -o $@ $^ -llapack -lm
	endif

shared: python_interface.c pgm.c svg.c elsdc.c gauss.c curve_grow.c polygon.c ring.c ellipse_fit.c rectangle.c iterator.c image.c lapack_wrapper.c misc.c
	ifeq ($(shell hostname),mercury)
	cc -c $(OPT) $(LIB) -fpic $^
	cc -shared $(OPT) $(LIB) -o libelsdc.so python_interface.o pgm.o svg.o elsdc.o gauss.o curve_grow.o polygon.o ring.o ellipse_fit.o rectangle.o iterator.o image.o lapack_wrapper.o misc.o -llapack -lm -lblas -lgfortran
	else
	cc -c $(OPT) $(LIB) -fpic $^
	cc -shared $(OPT) $(LIB) -o libelsdc.so python_interface.o pgm.o svg.o elsdc.o gauss.o curve_grow.o polygon.o ring.o ellipse_fit.o rectangle.o iterator.o image.o lapack_wrapper.o misc.o -llapack -lm
	endif

clean:
	rm elsdc
	rm *.o
	rm *.so
