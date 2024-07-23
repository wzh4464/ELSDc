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

# debug flag
# 新增 DEBUG 变量，默认为 0
DEBUG ?= 0

# 修改 OPT 变量
ifeq ($(DEBUG),1)
	OPT = -g -O0 -DDEBUG
else
	OPT = -O3
endif

# 通过shell命令uname来检测操作系统
UNAME_S := $(shell uname -s)

# lib extension
ifeq ($(UNAME_S), Darwin)
	LIB_EXTENSION = dylib
else
	LIB_EXTENSION = so
endif

# 检查发行版
ifeq ($(UNAME_S), Linux)
	IS_UBUNTU := $(shell grep -i ubuntu /etc/os-release > /dev/null && echo 1 || echo 0)
endif

# 根据操作系统设置特定的编译和链接选项
ifeq ($(UNAME_S), Darwin)
	# macOS
	LDFLAGS = -L/opt/homebrew/opt/lapack/lib
	CPPFLAGS = -I/opt/homebrew/opt/lapack/include
	LAPACK_FLAGS = -DUSE_LAPACKE
	LAPACK_LIBS = -llapacke -llapack -lblas
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
	cc -shared $(OPT) $(LDFLAGS) -o libelsdc.$(LIB_EXTENSION) *.o $(LAPACK_LIBS) -lm

clean:
	rm -f elsdc
	rm -f *.o
	rm -f *.so
	rm -f *.dylib
