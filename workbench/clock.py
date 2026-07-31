from PyQt5.QtCore import Qt
import yaml
import numpy as np
import cv2
from datetime import datetime
from math import pi, sin, cos
from random import randint

colors = []
colors.append(np.array([(v, v, v) for v in range(256)], dtype=np.uint8))
colors.append(np.array([(v*2, 0, 0) for v in range(128)] + [(255, v*2+1, v*2+1) for v in range(128)], dtype=np.uint8))
colors.append(np.array([(v*3, 0, 0) for v in range(85)] +
                       [(255, v*3, 0) for v in range(85)] +
                       [(255, 255, v*3) for v in range(86)] , dtype=np.uint8))
colors.append(np.array([(v*2, v*2, 0) for v in range(128)] + [(255, 255, v*2+1) for v in range(128)], dtype=np.uint8))
colors.append(np.array([(0, v*3, 0) for v in range(85)] +
                       [(v*3, 255, 0) for v in range(85)] +
                       [(255, 255, v*3) for v in range(86)] , dtype=np.uint8))
colors.append(np.array([(0, v*2, 0) for v in range(128)] + [(v*2+1, 255, v*2+1) for v in range(128)], dtype=np.uint8))
colors.append(np.array([(0, v*3, 0) for v in range(85)] +
                       [(0, 255, v*3) for v in range(85)] +
                       [(v*3, 255, 255) for v in range(86)] , dtype=np.uint8))
colors.append(np.array([(0, v*2, v*2) for v in range(128)] + [(v*2+1, 255, 255) for v in range(128)], dtype=np.uint8))
colors.append(np.array([(0, 0, v*3) for v in range(85)] +
                       [(0, v*3, 255) for v in range(85)] +
                       [(v*3, 255, 255) for v in range(86)] , dtype=np.uint8))
colors.append(np.array([(0, 0, v*2) for v in range(128)] + [(v*2+1, v*2+1, 255) for v in range(128)], dtype=np.uint8))
colors.append(np.array([(0, 0, v*3) for v in range(85)] +
                       [(v*3, 0, 255) for v in range(85)] +
                       [(255, v*3, 255) for v in range(86)] , dtype=np.uint8))
colors.append(np.array([(v*2, 0, v*2) for v in range(128)] + [(255, v*2+1, 255) for v in range(128)], dtype=np.uint8))
colors.append(np.array([(v*3, 0, 0) for v in range(85)] +
                       [(255, 0, v*3) for v in range(85)] +
                       [(255, v*3, 255) for v in range(86)] , dtype=np.uint8))

def draw_digit(canvas, digit, x, size, width):
  x += 1
  if digit == ":":
    cv2.circle(canvas, (x, int(size*0.45)), 2, 255)
    cv2.circle(canvas, (x, int(size*0.55)), 2, 255)
  else:
    lines = {"0": 119, "1": 36, "2": 93, "3": 109, "4": 46, "5": 107, "6": 123, "7": 37, "8": 127, "9": 111}
    if 1 & lines[digit]:
      cv2.line(canvas, (x, int(size*0.4)), (x + int(size*0.1), int(size*0.4)), 255, width)
    if 2 & lines[digit]:
      cv2.line(canvas, (x, int(size*0.4)), (x, int(size*0.5)), 255, width)
    if 4 & lines[digit]:
      cv2.line(canvas, (x + int(size*0.1), int(size*0.4)), (x + int(size*0.1), int(size*0.5)), 255, width)
    if 8 & lines[digit]:
      cv2.line(canvas, (x, int(size*0.5)), (x + int(size*0.1), int(size*0.5)), 255, width)
    if 16 & lines[digit]:
      cv2.line(canvas, (x, int(size*0.5)), (x, int(size*0.6)), 255, width)
    if 32 & lines[digit]:
      cv2.line(canvas, (x + int(size*0.1), int(size*0.5)), (x + int(size*0.1), int(size*0.6)), 255, width)
    if 64 & lines[digit]:
      cv2.line(canvas, (x, int(size*0.6)), (x + int(size*0.1), int(size*0.6)), 255, width)

def draw_clock(canvas, config):
  size = config["size"]
  now = datetime.now()

  if config["random"]["color"]["enabled"]:
    if not randint(0, config["random"]["color"]["chance"]):
      config["color"] = randint(0, len(colors) - 1)
  if config["random"]["wrap"]["enabled"]:
    if not randint(0, config["random"]["wrap"]["chance"]):
      config["wrap"] = not config["wrap"]

  if config["loop"]["enabled"]:
    config["loop"]["frame"] += 1
    if config["loop"]["frame"] > config["loop"]["duration"]:
      if config["loop"]["reverse"]:
        config["color"] = (config["color"] - 2) % 12 + 1
      else:
        config["color"] = config["color"] % 12 + 1
      config["loop"]["frame"] = 0

  if config["signal"]["enabled"]:
    if now.minute == config["signal"]["minute"] and now.second == 0:
      config["wrap"] = True
    elif now.minute == (config["signal"]["minute"] + 1) % 60 and now.second == 0:
      config["wrap"] = False
  
  if config["digital"]["shown"]:
    digits, cursor = (now.strftime("%H:%M:%S"), size*0.025) if config["digital"]["seconds"] else (now.strftime("%H:%M"), size*0.20)
    for digit in digits:
      draw_digit(canvas, digit, int(cursor), size, config["digital"]["width"])
      if digit == ":":
        cursor += size*0.05
      else:
        cursor += size*0.15

  if config["analog"]:
    if config["circle"]:
      cv2.circle(canvas, (size//2, size//2), int(size*0.47), 255)

    for minute in range(60):
      if minute % 5:
        if config["notches"]["minute"]["visible"]:
          cv2.line(canvas, (int(size//2 + sin(minute*pi/30)*size*0.47),
                            int(size//2 - cos(minute*pi/30)*size*0.47)),
                           (int(size//2 + sin(minute*pi/30)*size*(0.47-config["notches"]["minute"]["length"])),
                            int(size//2 - cos(minute*pi/30)*size*(0.47-config["notches"]["minute"]["length"]))), 255, 1)
      else:
        if config["notches"]["hour"]["visible"]:
          cv2.line(canvas, (int(size//2 + sin(minute*pi/30)*size*0.47),
                            int(size//2 - cos(minute*pi/30)*size*0.47)),
                           (int(size//2 + sin(minute*pi/30)*size*(0.47-config["notches"]["hour"]["length"])),
                            int(size//2 - cos(minute*pi/30)*size*(0.47-config["notches"]["hour"]["length"]))), 255, 1)

    if config["hour"]["visible"]:
      if config["hour"]["smooth"]:
        hour = now.hour + now.minute / 60 + now.second / 3600 + now.microsecond / 3600000000
      else:
        hour = now.hour
      cv2.line(canvas, (size//2, size//2), (int(size//2 + sin(hour*pi/6)*size*config["hour"]["length"]/2),
                                            int(size//2 - cos(hour*pi/6)*size*config["hour"]["length"]/2)), 255, config["hour"]["width"])

    if config["minute"]["visible"]:
      if config["minute"]["smooth"]:
        minute = now.minute + now.second / 60 + now.microsecond / 60000000
      else:
        minute = now.minute
      cv2.line(canvas, (size//2, size//2), (int(size//2 + sin(minute*pi/30)*size*config["minute"]["length"]/2),
                                            int(size//2 - cos(minute*pi/30)*size*config["minute"]["length"]/2)), 255, config["minute"]["width"])

    if config["second"]["visible"]:
      if config["second"]["smooth"]:
        second = now.second + now.microsecond / 1000000
      else:
        second = now.second
      cv2.line(canvas, (size//2, size//2), (int(size//2 + sin(second*pi/30)*size*config["second"]["length"]/2),
                                            int(size//2 - cos(second*pi/30)*size*config["second"]["length"]/2)), 255)

    if config["dots"]["visible"]:
      cv2.circle(canvas, (int(size//2 + sin(now.second*pi/30)*size*config["dots"]["distance"]/2),
                          int(size//2 - cos(now.second*pi/30)*size*config["dots"]["distance"]/2)), 2, 255)

def blur(canvas, config):
  size = config["size"]
  kernel = kernels(config)[config["kernel"]]
  blurred = np.zeros((size+2, size+2), dtype=np.uint16)
  blurred[1:-1,1:-1] = ((canvas[:-2,:-2]*kernel[0]  + canvas[:-2,1:-1]*kernel[1]  + canvas[:-2,2:]*kernel[2] +
                         canvas[1:-1,:-2]*kernel[3] + canvas[1:-1,1:-1]*kernel[4] + canvas[1:-1,2:]*kernel[5] +
                         canvas[2:,:-2]*kernel[6]   + canvas[2:,1:-1]*kernel[7]   + canvas[2:,2:]*kernel[8]) // sum(kernel))
  if config["fade"]:
    if config["wrap"]:
      blurred[1:-1,1:-1] -= config["fade"]
      blurred[blurred > 255] = 255
    else:
      blurred[blurred >= config["fade"]] -= config["fade"]
  return blurred

def get_sizes(config):
  return [int(s.strip()) for s in config["sizes"].split(",")]

def kernels(config):
  return [[int(v.strip()) for v in k.split(",")] for k in config["kernels"]]

def write_config(config):
  with open("clock.yaml", "w") as y:
    y.write(yaml.dump(config, sort_keys=False, default_flow_style=False))

def pos_to_str(pos):
  return f"{pos[0]},{pos[1]}"

def pos_from_str(pos):
  return tuple(int(c.strip()) for c in pos.split(","))

def handle_input(key, mod, config, window):
  match key:
    case Qt.Key_T:
      config["top"] = not config["top"]
      if config["top"]:
        window.setWindowFlag(Qt.WindowStaysOnTopHint)
        window.show()
      else:  
        window.setWindowFlag(Qt.WindowStaysOnTopHint, False)
        window.show()
    case Qt.Key_B:
      config["border"] = not config["border"]
      if config["border"]:
        window.setWindowFlag(Qt.FramelessWindowHint, False)
        window.show()
      else:  
        window.setWindowFlag(Qt.FramelessWindowHint)
        window.show()
    case Qt.Key_A:
      if config["analog"] and not config["digital"]["shown"]:
        config["digital"]["shown"] = True
      elif config["analog"] and config["digital"]["shown"]:
        config["analog"] = False
      else:
        config["digital"]["shown"] = False
        config["analog"] = True
      write_config(config)
      return config["size"]
    case Qt.Key_K:
      if mod & Qt.ShiftModifier:
        config["kernel"] = (config["kernel"] - 1) % len(kernels(config))
      else:
        config["kernel"] = (config["kernel"] + 1) % len(kernels(config))
    case Qt.Key_C:
      if mod & Qt.ShiftModifier:
        config["color"] = (config["color"] - 1) % len(colors)
      else:  
        config["color"] = (config["color"] + 1) % len(colors)
    case Qt.Key_O:
      config["circle"] = not config["circle"]
    case Qt.Key_R:
      if mod & Qt.ShiftModifier:
        config["random"]["wrap"]["enabled"] = not config["random"]["wrap"]["enabled"]
      else:
        config["random"]["color"]["enabled"] = not config["random"]["color"]["enabled"]
    case Qt.Key_L:
      if mod & Qt.ShiftModifier:
        if config["loop"]["enabled"]:
          if config["loop"]["reverse"]:
            config["loop"]["enabled"] = False
          else:
            config["loop"]["reverse"] = True
        else:
          config["loop"]["enabled"] = True
          config["loop"]["reverse"] = True
      else:
        if config["loop"]["enabled"]:
          if config["loop"]["reverse"]:
            config["loop"]["reverse"] = False
          else:
            config["loop"]["enabled"] = False
        else:
          config["loop"]["enabled"] = True
          config["loop"]["reverse"] = False
    case Qt.Key_N:
      if mod & Qt.ShiftModifier:
        config["notches"]["minute"] = not config["notches"]["minute"]
      else:
        config["notches"]["hour"] = not config["notches"]["hour"]
    case Qt.Key_H:
      if mod & Qt.ShiftModifier:
        config["hour"]["smooth"] = not config["hour"]["smooth"]
      else:
        config["hour"]["visible"] = not config["hour"]["visible"]
    case Qt.Key_M:
      if mod & Qt.ShiftModifier:
        config["minute"]["smooth"] = not config["minute"]["smooth"]
      else:
        config["minute"]["visible"] = not config["minute"]["visible"]
    case Qt.Key_S:
      if config["digital"]["shown"]:
        config["digital"]["seconds"] = not config["digital"]["seconds"]
      else:  
        if mod & Qt.ShiftModifier:
          config["second"]["smooth"] = not config["second"]["smooth"]
        else:  
          config["second"]["visible"] = not config["second"]["visible"]
    case Qt.Key_D:
      config["dots"]["visible"] = not config["dots"]["visible"]
    case Qt.Key_F:
      if mod & Qt.ShiftModifier:
        if config["fade"] > 0:
          config["fade"] = config["fade"] - 1
      else:
        if config["fade"] < 4:
          config["fade"] = config["fade"] + 1
    case Qt.Key_W:
      config["wrap"] = not config["wrap"]
    case Qt.Key_Period:
      sizes = get_sizes(config)
      if config["size"] in sizes:
        config["size"] = sizes[(sizes.index(config["size"])+1) % len(sizes)]
      else:
        config["size"] = 160
      write_config(config)
      return config["size"]
    case Qt.Key_Comma:
      sizes = get_sizes(config)
      if config["size"] in sizes:
        config["size"] = sizes[(sizes.index(config["size"])-1) % len(sizes)]
      else:
        config["size"] = 160
      write_config(config)
      return config["size"]
    case _:
      return
  write_config(config)
