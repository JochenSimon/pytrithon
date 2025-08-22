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

#declare Type = 6;

#switch (Type)
#case (0)
sphere { <0,0,0>,40 scale <1.66,1,1.25> texture {NBglass} pigment {rgbf <1+clock,0.2,0.2,0.5>} finish {phong .2 reflection {.3}}}
text { ttf "lucon.ttf" "malus" 0.1, 0 color rgbt <0,0,0,0.5> rotate <90,0,0> translate <-1.4,1,-0.3> scale <30,40,50> rotate <0,0,0>}
#break
#case (1)
sphere { <0,0,0>,40 scale <1.66,1,1.25> texture {NBglass} pigment {rgbf <0.8+clock*0.6,0.8+clock*0.6,0.2,0.5>} finish {phong .2 reflection {.3}}}
text { ttf "lucon.ttf" "slow" 0.1, 0 color rgbt <0,0,0,0.5> rotate <90,0,0> translate <-1.2,1,-0.3> scale <40,40,50> rotate <0,0,0>}
#break
#case (2)
sphere { <0,0,0>,40 scale <1.66,1,1.25> texture {NBglass} pigment {rgbf <0.2,0.8+clock,0.2,0.5>} finish {phong .2 reflection {.3}}}
text { ttf "lucon.ttf" "tiny" 0.1, 0 color rgbt <0,0,0,0.5> rotate <90,0,0> translate <-1.2,1,-0.3> scale <40,40,50> rotate <0,0,0>}
#break
#case (3)
sphere { <0,0,0>,40 scale <1.66,1,1.25> texture {NBglass} pigment {rgbf <0.2,0.8+clock,0.8+clock,0.5>} finish {phong .2 reflection {.3}}}
text { ttf "lucon.ttf" "fast" 0.1, 0 color rgbt <0,0,0,0.5> rotate <90,0,0> translate <-1.2,1,-0.3> scale <40,40,50> rotate <0,0,0>}
#break
#case (4)
sphere { <0,0,0>,40 scale <1.66,1,1.25> texture {NBglass} pigment {rgbf <0.2,0.2,2+clock,0.5>} finish {phong .2 reflection {.3}}}
text { ttf "lucon.ttf" "invul" 0.1, 0 color rgbt <0,0,0,0.5> rotate <90,0,0> translate <-1.4,1,-0.3> scale <30,40,50> rotate <0,0,0>}
#break
#case (5)
sphere { <0,0,0>,40 scale <1.66,1,1.25> texture {NBglass} pigment {rgbf <1+clock,0.2,1+clock,0.5>} finish {phong .2 reflection {.3}}}
text { ttf "lucon.ttf" "1UP" 0.1, 0 color rgbt <0,0,0,0.5> rotate <90,0,0> translate <-0.8,1,-0.3> scale <40,40,50> rotate <0,0,0>}
#break
#case (6)
sphere { <0,0,0>,40 scale <1.66,1,1.25> texture {NBglass} pigment {rgbf <1.5+clock*1,1.5+clock*1,1.5+clock*1,0.5>} finish {phong .2 reflection {.3}}}
text { ttf "lucon.ttf" "points" 0.1, 0 color rgbt <0,0,0,0.5> rotate <90,0,0> translate <-1.6,1,-0.3> scale <30,40,50> rotate <0,0,0>}
#break
#end

light_source {<100,120,130> White*2}
