#include <stdlib.h>
#include "pgm.h"
#include "ring.h"
#include "polygon.h"
#include "elsdc.h"

int detect_primitives(Ring **ell_out, int *ell_count, Polygon **poly_out,
  int *poly_count, int **out, double *in, size_t xsize, size_t ysize)
{
  PImageInt out_img;   /* output image having the same size as 'in'; the pixels
                          supporting a certain geometric primitive are marked
                          with the same label */
  int *ell_labels=NULL;/* the pixels supporting a certain ellipse are marked
                          with the same unique label */
  Ring *ell_out = NULL;/* array containing the parameters of the detected
                          ellipses; correlated with ell_labels, i.e. the i-th
                          element of ell_labels is the label of the pixels
                          supporting the ellipse defined by the parameters
                          ell[i] */
  int *poly_labels=NULL;/* the pixels supporting a certain polygon are marked
                          with the same unique label */
  Polygon *poly_out=NULL;/* array containing the parameters of the detected
                          polygons; correlated with poly_labels, i.e. the i-th
                          element of ell_labels is the label of the pixels
                          supporting the polygon defined by the parameters
                          poly[i] */
  struct ImageDouble in_img = {.data=in, .xsize=xsize, .ysize=ysize};
  out_img = new_PImageInt_ini(xsize, ysize, 0);
  ELSDc(&in_img, ell_count, ell_out, &ell_labels, poly_count, poly_out,
    &poly_labels, out_img);
  *out = out_img->data;
  return 0;
}
