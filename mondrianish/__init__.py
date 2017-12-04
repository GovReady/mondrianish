import argparse
import random
import sys

def generate_grid(canvas_size, density=.5):
  # Generate a Piet Mondrian-style image composed of rectangles of
  # various colors. This function generates the image in grid form
  # and returns the lines and rectangles that make up the image.
  #
  # The parameters are:
  #
  #    canvas_size: A tuple (width, height), where width and height
  #    are integers, generally small like (20, 20).
  #
  #    density (optional): How many rectangles should the grid
  #    be divided into? The default is 0.5 and raising or lowering
  #    it a bit will create more or fewer divisions.
  #
  # The return value is a tuple (lines, rectagles), each a list.
  # Each line and rectangle is of the form ((startx, starty), (endx, endy)).
  # The coordinates are integers in the range of (0, 0) to
  # (width-1, height-1).
  #
  # The key feature of these images is that they are made up of
  # horizontal and vertical line segments that terminate at the
  # canvas edges or at other line segments, leaving rectangular
  # open spaces in the middle to be filled in with various colors.
  #
  # Other programs that create Mondrian-style images tend to
  # recursively break up the canvas into pieces, as if it were a
  # fractal, but a general Mondrian-style image is not really
  # structured this way.
  #
  # So the technique here instead is to draw lines first, one after
  # another, only adding valid lines, and then afterward to see
  # how those lines break up the canvas into rectangles.

  if canvas_size[0] < 3 or canvas_size[1] < 3:
    raise ValueError("Canvas size must be at least 3-by-3.")

  # Start constructing line segments iteratively.
  lines = []
  for i in range(int((canvas_size[0]*canvas_size[1])**density)):
    # Shall we draw a vertical (0) or horizontal (1) line? Choose randomly.
    direction = random.choice([0, 1])

    # Pick a line segment perpendicular to our chosen direction
    # to be the left/top edge of the new segment, or start at the
    # left/top edge of the canvas (represented by "None").
    possible_starts = filter(
      lambda line :
        # only choose from perpendicular segments
        line["direction"] != direction,
      lines)
    lefttop = random.choice([None] + list(possible_starts))

    # Which lines can the new segment validly end at? Any
    # other perpendicular line to the right of or below the
    # start and that has some overlap in coordinates. Choose
    # randomly.
    possible_ends = filter(
      lambda line:
        # only choose from perpendicular segments
        line["direction"] != direction

        # and if we didn't choose the left/top edge, then also
        # check that...
        and (lefttop is None or 
          # the end line is to the right/below the start line
          (  line["x"] > lefttop["x"]
             # the two segments overlap in horizontal/vertical space
             # i.e. don't draw a line between these two line segments:
             #    ----
             # 
             #          ----
             and len(set(range(lefttop["y1"], lefttop["y2"]+1)) & set(range(line["y1"], line["y2"]+1))) > 0
             )),
      lines)
    rightbottom = random.choice([None] + list(possible_ends))

    # What coorindate should our new line be at? It can be at
    # any value within the canvas_size's dimensions, except on the
    # edges...
    possible_coordinates = set(range(1, canvas_size[direction]-1))

    # And it can't be to the left or right of either the start or
    # end segment, i.e. it must be able to touch each segment....
    if lefttop is not None: possible_coordinates &= set(range(lefttop["y1"]+1, lefttop["y2"]))
    if rightbottom is not None: possible_coordinates &= set(range(rightbottom["y1"]+1, rightbottom["y2"]))

    # And there may not be a segment there already or in a neighboring
    # coordinate, because then there's no area between them to fill.
    for line in lines:
      if line["direction"] == direction \
       and line["y1"] <= ((canvas_size[1-direction]-1) if rightbottom is None else rightbottom["x"]) \
       and line["y2"] >= (0 if lefttop is None else lefttop["x"]):
        possible_coordinates -= set([line["x"]-1, line["x"], line["x"]+1])

    if len(possible_coordinates) == 0:
      # Can't put a line here.
      continue

    # Choose a random location.
    coordinate = random.choice(list(possible_coordinates))

    # Add the line.
    lines.append({
      "direction": direction,
      "x": coordinate,
      "y1": 0 if lefttop is None else lefttop["x"],
      "y2": (canvas_size[1-direction]-1) if rightbottom is None else rightbottom["x"],
    })

  # Determine the rectangles from the lines. Start with a
  # single rectangle for the whole canvas_size and divide as
  # needed every time a line intersects a rectangle.
  rectangles = [((0,0), (canvas_size[0]-1, canvas_size[1]-1))]
  for line in lines:
    newrects = []
    for rect in rectangles:
      # Does this rectangle need to be divided?
      if line["direction"] == 0 \
         and rect[0][0] < line["x"] < rect[1][0] \
         and line["y1"] <= rect[0][1] \
         and line["y2"] >= rect[1][1]:
        newrects.append(((rect[0][0], rect[0][1]), (line["x"], rect[1][1])))
        newrects.append(((line["x"], rect[0][1]), (rect[1][0], rect[1][1])))
      elif line["direction"] == 1 \
         and rect[0][1] < line["x"] < rect[1][1] \
         and line["y1"] <= rect[0][0] \
         and line["y2"] >= rect[1][0]:
        newrects.append(((rect[0][0], rect[0][1]), (rect[1][0], line["x"])))
        newrects.append(((rect[0][0], line["x"]), (rect[1][0], rect[1][1])))
      else:
        newrects.append(rect)
    rectangles = newrects

  # Re-bake the lines to be in start-end coordinate form.
  lines = [
    ((line["x"], line["y1"]), (line["x"], line["y2"]))
      if line["direction"] == 0 else
    ((line["y1"], line["x"]), (line["y2"], line["x"]))
    for line in lines
  ]

  return (lines, rectangles)


def draw_as_ascii_art_grid(canvas_size, lines, rectangles):
  # Draw the grided lines and rectangles returned by generate_grid as
  # ASCII art. Returns two HEIGHTxWIDTH arrays of arrays, one for lines
  # and one for rectangles. The first, for lines, has an ASCII line
  # drawing character in each cell, or None if there is no line at the
  # character position. The second array, for rectangles, has an integer
  # indicating a color to draw at each character position, or None (if
  # there is a line there).

  # Draw rectangles to a HEIGHTxWIDTH array of array of character values.
  # Assign integers to the cells to represent the color to draw in that
  # character position.
  ascii_art_rects = [[None]*canvas_size[0] for _ in range(canvas_size[1])]
  for i, rect in enumerate(rectangles):
    for x in range(rect[0][0], rect[1][0]+1):
      for y in range(rect[0][1], rect[1][1]+1):
        ascii_art_rects[y][x] = i

  # Draw the lines to a HEIGHTxWIDTH array of array of length-one strings.
  # Assign an "X" to any position that a line should be drawn at, and leave
  # other cells empty.
  ascii_art_lines = [[None]*canvas_size[0] for _ in range(canvas_size[1])]
  for line in lines:
    for x in range(line[0][0], line[1][0]+1):
      for y in range(line[0][1], line[1][1]+1):
        ascii_art_lines[y][x] = "X"

  # Re-draw as ASCII line drawing characters depending on neighboring segments.
  ascii_art_lines_original = [list(row) for row in ascii_art_lines]
  def isline(x, y):
    if x < 0 or y < 0 or x >= canvas_size[0] or y >= canvas_size[1]:
      return False
    return ascii_art_lines_original[y][x]
  for x in range(canvas_size[0]):
    for y in range(canvas_size[1]):
      if isline(x, y):
        if isline(x-1, y) and isline(x+1, y) and isline(x, y-1) and isline(x, y+1):
          ascii_art_lines[y][x] = "┼"
        elif isline(x-1, y) and isline(x+1, y) and isline(x, y-1):
          ascii_art_lines[y][x] = "┴"
        elif isline(x-1, y) and isline(x+1, y) and isline(x, y+1):
          ascii_art_lines[y][x] = "┬"
        elif isline(x-1, y) and isline(x, y-1) and isline(x, y+1):
          ascii_art_lines[y][x] = "┤"
        elif isline(x+1, y) and isline(x, y-1) and isline(x, y+1):
          ascii_art_lines[y][x] = "├"
        elif isline(x-1, y) or isline(x+1, y):
          ascii_art_lines[y][x] = "─"
        elif isline(x, y-1) or isline(x, y+1):
          ascii_art_lines[y][x] = "│"

  return ascii_art_lines, ascii_art_rects


def draw_as_ascii_art(canvas_size):
  lines, rectangles = generate_grid(canvas_size)
  fill_shapes = "█▓▒░▮▯▞▙"
  ascii_art_lines, ascii_art_rects = draw_as_ascii_art_grid(canvas_size, lines, rectangles)
  for y in range(canvas_size[1]):
    for x in range(canvas_size[0]):
      if ascii_art_lines[y][x]:
        ascii_art_rects[y][x] = ascii_art_lines[y][x]
      else:
        ascii_art_rects[y][x] = fill_shapes[ascii_art_rects[y][x] % len(fill_shapes)]
  return "\n".join("".join(line) for line in ascii_art_rects)


def generate_to_console_curses(args):
  # Generates a Mondrian-style image in grid form, then renders
  # it as ASCII art using line drawing characters and displays
  # it uses curses to color the rectangles.

  def drawit(window):
    # Get the terminal size and generate image data using that
    # size for the grid.
    if not args.size:
      canvas_size = window.getmaxyx()
      canvas_size = (canvas_size[1], canvas_size[0]-1)
    else:
      canvas_size = args.size
    lines, rectangles = generate_grid(canvas_size)
    ascii_art_lines, ascii_art_rects = draw_as_ascii_art_grid(canvas_size, lines, rectangles)

    # init colors
    curses.init_pair(1, curses.COLOR_BLUE, curses.COLOR_BLUE)
    curses.init_pair(2, curses.COLOR_BLUE, curses.COLOR_CYAN)
    curses.init_pair(3, curses.COLOR_BLUE, curses.COLOR_GREEN)
    curses.init_pair(4, curses.COLOR_BLUE, curses.COLOR_MAGENTA)
    curses.init_pair(5, curses.COLOR_BLUE, curses.COLOR_RED)
    curses.init_pair(6, curses.COLOR_BLUE, curses.COLOR_WHITE)
    curses.init_pair(7, curses.COLOR_BLUE, curses.COLOR_YELLOW)

    window.clear()
    for y in range(canvas_size[1]):
      for x in range(canvas_size[0]):
        if ascii_art_lines[y][x]:
          window.addch(y, x, ascii_art_lines[y][x])
        else:
          color = (ascii_art_rects[y][x] % 7) + 1
          window.addch(y, x, " ", curses.color_pair(color))

    # wait
    window.getch()

  # Start.
  import curses
  curses.wrapper(drawit)


def generate_image(format, size, stroke_width, colors, stream):
  # Generate a Piet Mondrian-style image composed of rectangles of
  # various colors. Specify a format ("png" or "svg"), an output
  # size as a tuple (width, height), a stroke width for the lines,
  # an array of CSS colors (or None for default colors), and an
  # output file-like object opened in binary mode.

  import colour

  # Generate image data.
  grid_size = (int(round(size[0]/stroke_width/7)), int(round(size[1]/stroke_width/7)))
  if grid_size[0] < 3 or grid_size[1] < 3: raise ValueError("Stroke width is too large.")
  lines, rectangles = generate_grid(grid_size)

  # Prepare surface.
  if format == "png":
    from PIL import Image, ImageDraw
    im = Image.new("RGBA", size)
    draw = ImageDraw.Draw(im)
  elif format == "svg":
    # Make a PIL.Image-like class.
    class SvgImage:
      def __init__(self, size):
        self.data =  """<?xml version="1.0" encoding="UTF-8"?>\n"""
        self.data += """<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"
        width="{}px" height="{}px" viewBox="0 0 {} {}" version="1.1">\n""".format(
          size[0], size[1], size[0], size[1],
        )
        self.data += """<g id="surface1">\n"""
      def save(self, buffer, *args):
        self.data += """</g>\n"""
        self.data += """</svg>\n"""
        buffer.write(self.data.encode("utf8"))
    class SvgDraw:
      def __init__(self, im): self.im = im
      def rectangle(self, coords, fill):
        self.im.data += """<rect x="{x}" y="{y}" width="{width}" height="{height}" style="fill:{fill}" />\n""".format(
          x=coords[0][0],
          y=coords[0][1],
          width=coords[1][0]-coords[0][0],
          height=coords[1][1]-coords[0][1],
          fill="rgb({},{},{})".format(*fill)
        )
      def line(self, coords, fill, width):
        self.im.data += """<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" style="stroke:{fill};stroke-width:{width}" />\n""".format(
          x1=coords[0][0],
          y1=coords[0][1],
          x2=coords[1][0],
          y2=coords[1][1],
          fill="rgb({},{},{})".format(*fill),
          width=width
        )
    im = SvgImage(size)
    draw = SvgDraw(im)
  else:
    raise ValueError("Invalid format: {}.".format(format))

  # Normalizing grid size to the canvas.
  def scale_pt(p):
    return (int(round(p[0] * size[0]/(grid_size[0]-1))),
            int(round(p[1] * size[1]/(grid_size[1]-1))))

  # Helper functions.
  def draw_rectangle(box, color):
    draw.rectangle([scale_pt(box[0]), scale_pt(box[1])], fill=color)
  def draw_line(line, color, width):
    draw.line([scale_pt(line[0]), scale_pt(line[1])], fill=color, width=width)

  # Choose colors for the rectangles.
  fill_colors = []
  if colors is None:
    colors = ("#FFF8F0", "#FCAA67", "#7DB7C0", "#932b25", "#498B57")
  for color in colors:
      color = colour.Color(color)
      color = tuple([int(c*255) for c in color.rgb] + [255]) # => RGBA
      fill_colors.append(color)

  # Draw rectangles.
  for i, rect in enumerate(rectangles):
    # Choose a color.
    if True:
      # Assign in a rotation.
      color = fill_colors[i % len(fill_colors)]
    else:
      # Assign probabilistically with the earlier colors being more likely.
      color_samples = []
      for ii, color in enumerate(fill_colors): color_samples.extend([color]*(len(fill_colors)-ii)**2)
      color = random.choice(color_samples)

    # Draw.
    draw_rectangle(rect, color)

  # Draw lines.
  color = (20, 30, 40, 255) # Solid color
  width = int(round(stroke_width))
  for line in lines:
    draw_line(line, color, width)

  # Render.
  return im.save(stream, format)


# Entry point.

def main():
  def parse_width_height(s):
    ss = s.split("x")
    if len(ss) != 2: raise ValueError()
    return (int(ss[0]), int(ss[1]))
  parse_width_height.__name__ = "size"

  parser = argparse.ArgumentParser(description='Generate a Piet Mondrian-style image')
  parser.add_argument('format', type=str, nargs='?', default="console",
                      help='console (default), svg, png')
  parser.add_argument('--size', metavar='WIDTHxHEIGHT', type=parse_width_height,
                      help='width and height of the generated image')
  parser.add_argument('--stroke-width', metavar='THICKNESS', type=int, default=1,
                      help='thicknes of the lines')
  parser.add_argument('--color', metavar='#rrggbb', action="append",
                      help='colors to use (specify --color more than once)')

  args = parser.parse_args()

  if args.format == "console":
    generate_to_console_curses(args)
  elif args.format == "text":
    if not args.size:
      args.size = (60, 20)
    print(draw_as_ascii_art(args.size))
  elif args.format in ("svg", "png"):
    if not args.size:
      args.size = (800, 600)
    generate_image(args.format, args.size, args.stroke_width, args.color, sys.stdout.buffer)
  else:
    print("Invalid format:", args.format)
    sys.exit(1)

# Flask entry point.
try:
  from flask import Flask, send_file, Response, request
  app = Flask(__name__)

  @app.route("/image/<int:width>/<int:height>/<format>")
  def image_route(width, height, format):
    try:
      # Check incoming parameters.
      if width < 0 or width > 4096: raise ValueError("width is out of range")
      if height < 0 or height > 4096: raise ValueError("height is out of range")

      # Short-circuit for ASCII art output.
      if format == "text":
        canvas_size = (width, height)
        ascii_art = draw_as_ascii_art(canvas_size)
        return Response(ascii_art, mimetype="text/plain; charset=UTF-8")

      # Get additional parameters.
      stroke_width = int(request.args.get("stroke-width", str(round(((width+height)**.5/10)+1))))
      colors = None
      if request.args.get("colors"):
        colors = request.args.get("colors", "").split(";")

      # Generate image.
      import io
      buf = io.BytesIO()
      generate_image(format, (width, height), stroke_width, colors, buf)
      buf.seek(0)

      # Form response.
      if format == "png":
        mimetype = "image/png"
      elif format == "svg":
        mimetype = "image/svg+xml"
      return send_file(buf, mimetype=mimetype)

    except ValueError as e:
      return str(e)

except ImportError:
  pass

if __name__ == "__main__":
  main()
