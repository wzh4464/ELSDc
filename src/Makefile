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

# 通过shell命令uname来检测操作系统
UNAME_S := $(shell uname -s)

# 设置默认编译选项
OPT = -O3

# 检查发行版
IS_UBUNTU := $(shell grep -i ubuntu /etc/os-release > /dev/null && echo 1 || echo 0)

# 根据操作系统设置特定的编译和链接选项
ifeq ($(UNAME_S), Darwin)
	# macOS
	LDFLAGS = -L/opt/homebrew/opt/lapack/lib
	CPPFLAGS = -I/opt/homebrew/opt/lapack/include
	LAPACK_FLAGS = -DUSE_LAPACKE
	LAPACK_LIBS = -llapacke
else ifeq ($(UNAME_S), Linux)
	ifeq ($(IS_UBUNTU), 1)
		# Ubuntu
		LDFLAGS = -L/usr/lib/x86_64-linux-gnu
		CPPFLAGS = -I/usr/include
		LAPACK_FLAGS = -DUSE_LAPACKE
		LAPACK_LIBS = -llapacke -llapack -lblas
	else
		# CentOS
		LDFLAGS = -L/home/zihan/lib
		CPPFLAGS = -I/home/zihan/include
		LAPACK_LIBS = -llapack -lblas -lgfortran
	endif
else
	$(error Unsupported platform)
endif

elsdc: main.c pgm.c svg.c elsdc.c gauss.c curve_grow.c polygon.c ring.c ellipse_fit.c rectangle.c iterator.c image.c lapack_wrapper.c misc.c
	cc $(OPT) $(CPPFLAGS) $(LDFLAGS) $(LAPACK_FLAGS) -o $@ $^ $(LAPACK_LIBS) -lm

shared: python_interface.c pgm.c svg.c elsdc.c gauss.c curve_grow.c polygon.c ring.c ellipse_fit.c rectangle.c iterator.c image.c lapack_wrapper.c misc.c
	cc -c $(OPT) $(CPPFLAGS) $(LAPACK_FLAGS) -fpic $^
	cc -shared $(OPT) $(CPPFLAGS) $(LDFLAGS) $(LAPACK_FLAGS) -o libelsdc.so python_interface.o pgm.o svg.o elsdc.o gauss.o curve_grow.o polygon.o ring.o ellipse_fit.o rectangle.o iterator.o image.o lapack_wrapper.o misc.o $(LAPACK_LIBS) -lm

clean:
	rm -f elsdc
	rm -f *.o
	rm -f *.so
