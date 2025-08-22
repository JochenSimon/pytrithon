import sys
from PIL import Image

if sys.argv[1] == "extra":
  images = [[Image.open(f"{type}{i}.png") for i in range(9)] for type in ("malus", "slow", "tiny", "fast", "invul", "1up", "points")]

  new_im = Image.new("RGBA", (64*16, 32*7))

  for i,t in enumerate(images):
    for j,im in enumerate(t):
      if 1 <= j <= 7:
        new_im.paste(im, (64*16 - j*64, i*32))
      new_im.paste(im, (j*64, i*32))

  new_im.save("extra.png")

if sys.argv[1] == "money":
  images = [[Image.open(f"{type}{i}.png") for i in range(9)] for type in ("one", "five", "twenty", "fifty")]

  new_im = Image.new("RGBA", (80*16, 80*4))

  for i,t in enumerate(images):
    for j,im in enumerate(t):
      if 1 <= j <= 7:
        new_im.paste(im, (80*16 - j*80, i*80))
      new_im.paste(im, (j*80, i*80))

  new_im.save("money.png")

if sys.argv[1] == "sphere":
  images = [[Image.open(f"sphere{i}.png") for i in range(9)]]

  new_im = Image.new("RGBA", (48*16, 48))

  for i,t in enumerate(images):
    for j,im in enumerate(t):
      if 1 <= j <= 7:
        new_im.paste(im, (48*16 - j*48, i*48))
      new_im.paste(im, (j*48, i*48))

  new_im.save("sphere.png")

if sys.argv[1] == "spheresmall":
  images = [[Image.open(f"spheresmall{i}.png") for i in range(9)]]

  new_im = Image.new("RGBA", (32*16, 32))

  for i,t in enumerate(images):
    for j,im in enumerate(t):
      if 1 <= j <= 7:
        new_im.paste(im, (32*16 - j*32, i*32))
      new_im.paste(im, (j*32, i*32))

  new_im.save("spheresmall.png")

if sys.argv[1] == "spherebig":
  images = [[Image.open(f"spherebig{i}.png") for i in range(9)]]

  new_im = Image.new("RGBA", (64*16, 64))

  for i,t in enumerate(images):
    for j,im in enumerate(t):
      if 1 <= j <= 7:
        new_im.paste(im, (64*16 - j*64, i*64))
      new_im.paste(im, (j*64, i*64))

  new_im.save("spherebig.png")

if sys.argv[1] == "snake":
  images = [[Image.open(f"snake{i}.png") for i in range(9)]]

  new_im = Image.new("RGBA", (160*16, 32))

  for i,t in enumerate(images):
    for j,im in enumerate(t):
      if 1 <= j <= 7:
        new_im.paste(im, (160*16 - j*160, i*32))
      new_im.paste(im, (j*160, i*32))

  new_im.save("snake.png")

if sys.argv[1] == "missile":
  images = [[Image.open(f"missile{i:02}.png") for i in range(16)]]

  new_im = Image.new("RGBA", (64*16, 32))

  for i,t in enumerate(images):
    for j,im in enumerate(t):
      new_im.paste(im, (j*64, i*32))

  new_im.save("missile.png")

