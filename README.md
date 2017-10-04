Mandorianish
============

A Python module that generates a [Piet Mondrian-style image](https://en.wikipedia.org/wiki/Piet_Mondrian#Paris_.281919.E2.80.931938.29)
composed of rectangles of various colors and dark lines between them.

Other programs that create Mondrian-style images tend to recursively break up the canvas
into pieces, as if it were a fractal, but a general Mondrian-style image is not really
structured this way. The technique here instead is to draw lines first, adding only
horizontal and vertical lines that terminate at the edge of the canvas or at another
line, and then afterward seeing how those lines break up the canvas into rectangles.

Run the module directly from a Unix console to display a randomly generated image on
the console (using `curses`):

	python3 mondrianish.py

It will show something like:

![Screenshot](screenshot.png)

(Press any key to exit.)

You can also render the image to a file by specifying a file format and size:

	pip3 install pycairo colour
	python3 mondrianish.py --size 800x600 svg > image.svg

<center>

![Sample](sample.png)

</center>

You can also specify:

`--color red --color blue ...` for colors. Use CSS colors (`#AA5590`) or anything [colour](https://pypi.python.org/pypi/colour) can parse from a string. Defaults will be used if not specified.

You can also run it as a Flask app:

	pip3 install Flask
	FLASK_APP=mondrianish.py flask run

Then visit `http://127.0.0.1:5000/image/{width}/{height}/{format}` to download images, like [http://127.0.0.1:5000/image/128/128/png](http://127.0.0.1:5000/image/1280/1280/png).