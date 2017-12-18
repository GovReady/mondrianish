import unittest

import io
import random

from mondrianish import generate_grid, draw_as_ascii_art, generate_image

class TestMondrianish(unittest.TestCase):

    def setUp(self):
        random.seed("remove randomness from images so test images produce consistent output")

    def test_six_by_six_default_density(self):
        lines, rects = generate_grid((6, 6))
        self.assertEqual(lines, [((4, 0), (4, 5)), ((1, 0), (1, 5)), ((1, 1), (5, 1))])
        self.assertEqual(rects, [((0, 0), (1, 5)), ((1, 0), (4, 1)), ((1, 1), (4, 5)), ((4, 0), (5, 1)), ((4, 1), (5, 5))])

    def test_draw_as_ascii_art(self):
        image = draw_as_ascii_art((6, 6))
        self.assertEqual(image, '█│▓▓│▒\n█│▓▓│▒\n█│▓▓│▒\n█│▓▓│▒\n█│▓▓│▒\n█│▓▓│▒')

    def test_draw_image(self):
        buf = io.BytesIO()
        generate_image('svg', (75, 50), 2, ('red', 'green'), buf)
        self.assertEqual(buf.getvalue(), b'<?xml version="1.0" encoding="UTF-8"?>\n<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"\n        width="75px" height="50px" viewBox="0 0 75 50" version="1.1">\n<g id="surface1">\n<rect x="0" y="0" width="38" height="33" style="fill:rgb(255,0,0)" />\n<rect x="0" y="33" width="38" height="17" style="fill:rgb(0,128,0)" />\n<rect x="38" y="0" width="37" height="50" style="fill:rgb(255,0,0)" />\n<line x1="38" y1="0" x2="38" y2="50" style="stroke:rgb(20,30,40);stroke-width:2" />\n<line x1="0" y1="33" x2="38" y2="33" style="stroke:rgb(20,30,40);stroke-width:2" />\n</g>\n</svg>\n')



if __name__ == '__main__':
    unittest.main()
