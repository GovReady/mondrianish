function random_element(array) {
  return array[Math.floor(Math.random() * array.length)];
}

function generate_grid(canvas_size, density) {
  /*
  Generate a Piet Mondrian-style image composed of rectangles of
  various colors. This function generates the image in grid form
  and returns the lines and rectangles that make up the image.
  
  The parameters are:
  
  canvas_size: An array [width, height], where width and height
  are integers, generally small like [20, 20].
  
  density: How many rectangles should the grid
  be divided into? The default is 0.5 and raising or lowering
  it a bit will create more or fewer divisions.
  
  The return value is an object { lines: ..., rectagles: ...}, each an array.
  Each line and rectangle is of the form [[startx, starty], [endx, endy]].
  The coordinates are integers in the range of (0, 0) to
  (width-1, height-1).
  
  The key feature of these images is that they are made up of
  horizontal and vertical line segments that terminate at the
  canvas edges or at other line segments, leaving rectangular
  open spaces in the middle to be filled in with various colors.
  
  Other programs that create Mondrian-style images tend to
  recursively break up the canvas into pieces, as if it were a
  fractal, but a general Mondrian-style image is not really
  structured this way.
  
  So the technique here instead is to draw lines first, one after
  another, only adding valid lines, and then afterward to see
  how those lines break up the canvas into rectangles.
  */

  if (canvas_size[0] < 3 || canvas_size[1] < 3)
    throw "Canvas size must be at least 3-by-3.";

  if (typeof density === "undefined")
    density = .5;

  // Start constructing line segments iteratively.
  var lines = [];
  for (var i = 0; i < (canvas_size[0]*canvas_size[1])**density; i++) {
    // Shall we draw a vertical (0) or horizontal (1) line? Choose randomly.
    var direction = random_element([0, 1])

    // Pick a line segment perpendicular to our chosen direction
    // to be the left/top edge of the new segment, or start at the
    // left/top edge of the canvas (represented by null).
    var possible_starts = lines.filter(function(line) { return line.direction != direction });
    var lefttop = random_element([null].concat(possible_starts));

    // Which lines can the new segment validly end at? Any
    // other perpendicular line to the right of or below the
    // start and that has some overlap in coordinates. Choose
    // randomly.
    function intervals_overalp(a1, a2, b1, b2) {
      return (a1 <= b1 && b1 <= a2) || (a1 <= b2 && b2 <= a2) || (b1 <= a1 && a1 <= b2) || (b1 <= a2 && a2 <= b2);
    }
    var possible_ends = lines.filter(function(line) {
        return line.direction != direction
                && (lefttop === null
                  || (line.x > lefttop.x && intervals_overalp(lefttop.y1, lefttop.y2, line.y1, line.y2))); });
    var rightbottom = random_element([null].concat(possible_ends));

    // What coorindate should our new line be at? It can be at
    // any value within the canvas_size's dimensions, except on the
    // edges...
    var coordrange = [1, canvas_size[direction]-1];

    // And it can't be to the left or right of either the start or
    // end segment or exactly on their ends...
    if (lefttop !== null)
      coordrange = [Math.max(coordrange[0], lefttop.y1+1), Math.min(coordrange[1], lefttop.y2-1)];
    if (rightbottom !== null)
      coordrange = [Math.max(coordrange[0], rightbottom.y1+1), Math.min(coordrange[1], rightbottom.y2-1)];

    // Turn the range into a sequence of integers of possible good locations
    // that we'll randomly draw from.
    if (coordrange[1] < coordrange[0])
      continue;
    var possible_coordinates = new Array(coordrange[1]-coordrange[0]+1).fill(0).map(function(x,i) { return coordrange[0] + i; });

    // And there may not be a segment there already or in a neighboring
    // coordinate, because then there's no area between them to fill.
    lines.forEach(function(line) {
      if ( line.direction == direction
       && (rightbottom === null ? true : line.y1 <= rightbottom.x)
       && (lefttop === null ? true : line.y2 >= lefttop.x))
        for (var x = line.x-1; x <= line.x+1; x++) {
          // Remove x.
          var idx = possible_coordinates.indexOf(x);
          if (idx != -1) possible_coordinates.splice(idx, 1);
        }
    });

    // Can't put a line here?
    if (possible_coordinates.length == 0)
      continue;

    // Choose a random location.
    var coordinate = random_element(possible_coordinates);

    // Add the line.
    lines.push({
      direction: direction,
      x: coordinate,
      y1: lefttop === null ? 0 : lefttop.x,
      y2: rightbottom === null ? (canvas_size[1-direction]-1) : rightbottom.x
    });
  }

  // Determine the rectangles from the lines. Start with a
  // single rectangle for the whole canvas_size and divide as
  // needed every time a line intersects a rectangle.
  var rectangles = [[[0,0], [canvas_size[0]-1, canvas_size[1]-1]]]
  lines.forEach(function(line) {
    rectangles.forEach(function(rect) {
      // Does this rectangle need to be divided?
      if (rect.killed)
        return;
      if (line.direction == 0
         && rect[0][0] < line.x && line.x < rect[1][0]
         && line.y1 <= rect[0][1]
         && line.y2 >= rect[1][1]) {
        rectangles.push([[rect[0][0], rect[0][1]], [line.x, rect[1][1]]]);
        rectangles.push([[line.x, rect[0][1]], [rect[1][0], rect[1][1]]]);
        rect.killed = true;
      } else if (line.direction == 1
         && rect[0][1] < line.x && line.x < rect[1][1]
         && line.y1 <= rect[0][0]
         && line.y2 >= rect[1][0]) {
        rectangles.push([[rect[0][0], rect[0][1]], [rect[1][0], line.x]]);
        rectangles.push([[rect[0][0], line.x], [rect[1][0], rect[1][1]]]);
        rect.killed = true;
      }
    });
  });
  rectangles = rectangles.filter(function(rect) { return !rect.killed; });

  // Re-bake the lines to be in start-end coordinate form.
  lines = lines.map(function(line) {
    return (line.direction == 0
          ? [[line.x, line.y1], [line.x, line.y2]]
          : [[line.y1, line.x], [line.y2, line.x]]);
  });

  return { lines: lines, rectangles: rectangles };
}

