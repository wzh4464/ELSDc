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

# macos use dylib, linux use so
UNAME_S := $(shell uname -s)

ifeq ($(UNAME_S), Darwin)
	LIB_EXTENSION = dylib
else
	LIB_EXTENSION = so
endif

#  pass debug flag to the low-level makefile
# e.g. make shared DEBUG=1
DEBUG ?= 0

elsdc:
	make -C src DEBUG=$(DEBUG)
	mv src/elsdc .

shared:
	make -C src shared DEBUG=$(DEBUG)
	mv -f src/libelsdc.$(LIB_EXTENSION) .

test:
	./elsdc shapes.pgm

clean:
	rm -f elsdc
	rm -f libelsdc.$(LIB_EXTENSION)
	rm -f src/*.o
