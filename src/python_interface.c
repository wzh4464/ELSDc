#include <stdlib.h>
#include "pgm.h"
#include "ring.h"
#include "polygon.h"
#include "elsdc.h"

extern int detect_primitives(Ring **ell_out, int **ell_labels, int *ell_count, 
  Polygon **poly_out, int **poly_labels, int *poly_count, 
  int **out, double *in, size_t xsize, size_t ysize)
{
  PImageInt out_img;   /* output image having the same size as 'in'; the pixels
                          supporting a certain geometric primitive are marked
                          with the same label */
  struct ImageDouble in_img = {.data=in, .xsize=xsize, .ysize=ysize};
  out_img = new_PImageInt_ini(xsize, ysize, 0);
  ELSDc(&in_img, ell_count, ell_out, ell_labels, poly_count, poly_out,
    poly_labels, out_img);
  *out = out_img->data;
  free(out_img);
  return 0;
}

extern void free_outputs(Ring *ell_out, int *ell_labels, 
  Polygon *poly_out, int *poly_labels, int poly_count, int *out)
{
  if(ell_out){
    free(ell_out);
    free(ell_labels);
  }
  if(poly_out){
    for(int i = 0; i < poly_count; i++){
      free(poly_out[i].pts);
    }
    free(poly_out);
    free(poly_labels);
  }
  if(out){
    free(out);
  }
}
