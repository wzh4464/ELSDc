/*------------------------------------------------------------------------------

  Copyright (c) 2014 viorica patraucean (vpatrauc@gmail.com)
  
  This program is free software: you can redistribute it and/or modify
  it under the terms of the GNU Affero General Public License as
  published by the Free Software Foundation, either version 3 of the
  License, or (at your option) any later version.

  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
  GNU Affero General Public License for more details.

  You should have received a copy of the GNU Affero General Public License
  along with this program. If not, see <http://www.gnu.org/licenses/>.


  lapack_wrapper.c - This file belongs to ELSDc project (Ellipse and Line 
                     Segment Detector with continuous validation).
                   - It contains wrappers for lapack functions.

------------------------------------------------------------------------------*/

#ifdef __APPLE__
#include <lapacke.h>
#define dsyev LAPACKE_dsyev
#include <stdio.h>
// 添加其他需要重定义的LAPACK函数
#else
#include <lapack.h>
#endif

#include "lapack_wrapper.h"

typedef long int integer;
typedef double doublereal;


/*----------------------------------------------------------------------------*/
/** Header of lapack function for computing the eigen-decomposition of a
    matrix of double. 
 */
// void dsyev(char *jobz, char *uplo, integer *n, doublereal *a, 
//            integer *lda, doublereal *w, doublereal *work, integer *lwork, 
//            integer *info);


/*----------------------------------------------------------------------------*/
/** Solve linear system. 
    'n' number of unknowns;
    'A' coefficients of the equations. 
 */
void lap_eig(double *A, int n) 
{
#ifdef __APPLE__
    // macOS 版本使用 LAPACKE 接口
    int info;
    info = LAPACKE_dsyev(LAPACK_COL_MAJOR, 'V', 'U', n, A, n, A + n*n);
    if (info != 0) {
        fprintf(stderr, "LAPACKE_dsyev failed with error %d\n", info);
    }
#else
    // 其他系统使用原始 LAPACK 接口
    char jobz = 'V';
    char uplo = 'U';
    integer M = (integer)n;
    integer LDA = M;
    integer LWORK = 24;
    integer INFO;
    doublereal W[6];
    doublereal WORK[LWORK];
    
    dsyev_(&jobz, &uplo, &M, (doublereal*)A, &LDA, W, WORK, &LWORK, &INFO);
    
    if (INFO != 0) {
        fprintf(stderr, "dsyev_ failed with error %d\n", (int)INFO);
    }
#endif
}