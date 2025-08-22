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

#declare Type = 3;

#switch (Type)
#case (0)
torus { 40,1 scale <1.63,1,1.22> texture {NBglass} pigment {rgbf <0.2,1.5+clock*2,0.2,0.5>} finish {phong .2 reflection {.3}}}
#break
#case (1)
torus { 40,1 scale <1.63,1,1.22> texture {NBglass} pigment {rgbf <0.2,0.2,1.5+clock*2,0.5>} finish {phong .2 reflection {.3}}}
#break
#case (2)
torus { 40,1 scale <1.63,1,1.22> texture {NBglass} pigment {rgbf <1.5+clock*2,0.2,0.2,0.5>} finish {phong .2 reflection {.3}}}
#break
#case (3)
torus { 40,1 scale <1.63,1,1.22> texture {NBglass} pigment {rgbf <1.5+clock*2,0.2,1.5+clock*2,0.5>} finish {phong .2 reflection {.3}}}
#break
#end

light_source {<100,120,130> White*2}
