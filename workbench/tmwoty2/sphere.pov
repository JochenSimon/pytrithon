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

sphere { <0,0,0>,40 scale <1.66,1,1.25> texture {NBglass} pigment {rgbf <2+clock*0.5,2+clock*0.5,2+clock*0.5,0.5>} finish {phong .2 reflection {.3}}}

light_source {<100,120,130> White*2}
