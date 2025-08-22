#version 3.7;
global_settings {charset utf8 assumed_gamma 1.0}

#include "colors.inc"
#include "textures.inc"

camera {
  orthographic
  location <0,100,0>
  look_at <0,0,0>
}

background {color rgbt <0,0,0,1>}

union {
  #if (clock < 0.5)
  sphere { <24,0,0>,16 texture {NBglass} pigment {rgbf <2,0,clock*4,0.5>} finish {phong .2 reflection {.3}}}
  #else
  sphere { <24,0,0>,16 texture {NBglass} pigment {rgbf <2,0,2-(clock-0.5)*4,0.5>} finish {phong .2 reflection {.3}}}
  #end
  cylinder { <-40,0,0>, <24,0,0>,16 texture {Chrome_Metal} }
  box { <-40,-40,-1>, <-24,40,1> texture {Chrome_Metal} }
  box { <-40,-40,-1>, <-24,40,1> texture {Chrome_Metal} rotate x*90}
  rotate x*90*clock*0.9375 scale <1.66,1,1.25> 
}

light_source {<100,120,130> White*2}
