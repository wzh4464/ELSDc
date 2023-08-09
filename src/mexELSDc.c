#include "mex.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "misc.h"
#include "pgm.h"
#include "svg.h"
#include "polygon.h"
#include "ring.h"
#include "elsdc.h"

void mexFunction(int nlhs, mxArray *plhs[], int nrhs, const mxArray *prhs[])
{
    /* check arguments */
    if( nrhs < 1 ) mexErrMsgTxt("usage: mexELSDc('imagename.pgm')");

    PImageDouble in;     /* input image */
    PImageInt    out;    /* output image having the same size as 'in'; the pixels
                          supporting a certain geometric primitive are marked 
                          with the same label */

    int ell_count = 0;   /* number of detected ellipses */
    int *ell_labels=NULL;/* the pixels supporting a certain ellipse are marked 
                          with the same unique label */
    Ring *ell_out = NULL;/* array containing the parameters of the detected 
                          ellipses; correlated with ell_labels, i.e. the i-th
                          element of ell_labels is the label of the pixels 
                          supporting the ellipse defined by the parameters 
                          ell[i] */
                       
    int poly_count = 0;  /* number of detected polygons */
    int *poly_labels=NULL;/* the pixels supporting a certain polygon are marked 
                          with the same unique label */
    Polygon *poly_out=NULL;/* array containing the parameters of the detected 
                          polygons; correlated with poly_labels, i.e. the i-th
                          element of ell_labels is the label of the pixels 
                          supporting the polygon defined by the parameters
                          poly[i] */

    FILE *ell_ascii;     /* output file with the parameters of the detected 
                          ellipses -- ASCII format */
    FILE *poly_ascii;    /* output file with the parameters of the detected
                          polygons -- ASCII format */
    FILE *fsvg;          /* output file with the detected ellipses and polygons 
                          in vectorial form */
    int i,j;
    char sourcename[100], name[100], outname[100], svgname[100], pgmname[100];

    /* read input image; must be PGM form */
    strcpy(sourcename,mxArrayToString(prhs[0]));
    // name is sourcename without the extension
    strcpy(name, sourcename);
    char* ext = strrchr(name, '.');
    if (ext != NULL) *ext = '\0';

    in = read_pgm_image_double( sourcename );
    int xsize = in->xsize, ysize = in->ysize;
  
    /* create and initialize with 0 output label image */
    out = new_PImageInt_ini( in->xsize, in->ysize, 0 );  
  
    /* second output is a int matrix */
    plhs[2] = mxCreateNumericMatrix(ysize, xsize, mxINT32_CLASS, mxREAL);
    out->data = (int *) mxGetData(plhs[2]);
    mexPrintf("xsize: %d, ysize: %d\n", xsize, ysize);

    /* call detection procedure */
    ELSDc( in, &ell_count, &ell_out, &ell_labels, &poly_count, &poly_out, 
         &poly_labels, out );

    /* write results in ASCII */
    /* Ellipse file: each line contains 1 integer and 11 doubles in the form
     ell_label x1 y1 x2 y2 cx cy ax bx theta ang_start ang_end
     where:
     ell_label          -- the label of the pixels supporting this ellipse in 
                           'out' labels image 
     x1, y1, x2, y2     -- points delimiting the arc in trigonometric sense
     cx, cy             -- center of the ellipse
      ax, bx             -- the lengths of the semi-major and semi-minor axes
      theta              -- the angle between the semi-major axis and the x-axis
      ang_start, ang_end -- the angles delimiting the arc in trigonometric sense
    */

    if( ell_out != NULL )
    {
        strcpy(outname, name);
        if( (ell_ascii = fopen(strcat(outname,"_out_ellipse.txt"),"w")) == NULL )
            error("main: can't open ellipse output file.");
        /* return ell_out(5:) */
        plhs[0] = mxCreateDoubleMatrix(ell_count, 7, mxREAL);
        plhs[1] = mxCreateDoubleMatrix(ell_count, 1, mxREAL);
        double *out_data = mxGetPr(plhs[0]);
        double *out_label = mxGetPr(plhs[1]);
        for( i=0; i<ell_count; i++ )
        {
          fprintf( ell_ascii,"%d ", ell_labels[i] );
          fprintf( ell_ascii,"%lf %lf %lf %lf %lf %lf %lf %lf %lf %lf %lf \n",
                   ell_out[i].x1, ell_out[i].y1, ell_out[i].x2, ell_out[i].y2, 
                   ell_out[i].cx, ell_out[i].cy, ell_out[i].ax, ell_out[i].bx,
                   ell_out[i].theta, ell_out[i].ang_start, ell_out[i].ang_end );
          /* return ell_out(5:) */
          out_data[i] = ell_out[i].x1;
          out_data[i + ell_count] = ell_out[i].y1;
          out_data[i + 2 * ell_count] = ell_out[i].x2;
          out_data[i + 3 * ell_count] = ell_out[i].y2;
          out_data[i + 4 * ell_count] = ell_out[i].cx;
          out_data[i + 5 * ell_count] = ell_out[i].cy;
          out_data[i + 6 * ell_count] = ell_out[i].theta;
          out_label[i] = ell_labels[i];
        }
        fclose(ell_ascii);
    }

  /* Polygon file: each line contains 2 integers and a variable number of  
     doubles in the form 
     poly_label n x1 y1 x2 y2 ... xn yn
     where:
     poly_label      -- the label of the pixels supporting this polygon in 
                        'out' labels image
     n               -- the number of points in the polygon; it is the double 
                        of the number of segments
     x1 y1 ... xn yn -- (x,y) coordinates of the ending points of each segment.
     A polygon with n/2 line segments has n points, given in consecutive order.
   */
// if( poly_out != NULL )
//     {
//       if( (poly_ascii = fopen("out_polygon.txt","w")) == NULL )
//         error("main: can't open polygon output file.");
//       for( i=0; i<poly_count; i++ )
//         {
//           fprintf( poly_ascii, "%d %d ", poly_labels[i], poly_out[i].dim );
//           for( j=0; j<poly_out[i].dim; j++ )
//             fprintf( poly_ascii,"%lf %lf ", poly_out[i].pts[j].x, poly_out[i].pts[j].y);
//           fprintf( poly_ascii, "\n" );
//         }
//       fclose(poly_ascii);
//     }  
  // name = strcat("../toPGM/", name);
  /* write vectorial output in SVG format */
  if( (ell_out != NULL) || (poly_out != NULL) )
    {
      /* init svg file */
      // fsvg = init_svg( "output.svg", xsize, ysize );
      strcpy(svgname, name);
      fsvg = init_svg( strcat(svgname, ".svg"), xsize, ysize );
 
      /* write ellipses */
      for( i=0; i<ell_count; i++)
        /* distinguish between circle and ellipse, because the procedures 
           to write them are different */
        if( (double_equal( ell_out[i].ax, ell_out[i].bx )) )/* && (ell_out[i].theta == 0) ) */
          write_svg_circ_arc( fsvg, &ell_out[i] );
        else 
          write_svg_ell_arc( fsvg, &ell_out[i] );
        
      /* write polygons */
      for( i=0; i<poly_count; i++ )
        write_svg_poly( fsvg, &poly_out[i] );
      /* close svg file */
      fclose_svg( fsvg );
    }

  /* write labels image in pgm form */
  // write_pgm_image_int( out->data, out->xsize, out->ysize, "labels.pgm" );
  // strcpy(pgmname, name);
  // write_pgm_image_int( out->data, out->xsize, out->ysize, strcat(pgmname, "_labels.pgm"));
  // free_PImageInt(out);
  if( ell_out != NULL ) {free(ell_out); free(ell_labels);}
  if( poly_out != NULL ) 
    {
      for( i=0; i<poly_count; i++ )
        free(poly_out[i].pts);
      free(poly_out); 
      free(poly_labels);
    }
    mexPrintf("Number of ellipses: %d\n", ell_count );
    mexPrintf("Number of polygons: %d\n", poly_count );
    nlhs = 3;
}