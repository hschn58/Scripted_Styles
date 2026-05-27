import numpy as np
from PIL import Image
import tempfile
import os


def test_crop_to_square():
    from designs.utils.crop_precisely import crop_to_square

    with tempfile.TemporaryDirectory() as tmpdir:
        img = Image.new("RGB", (200, 100), color="red")
        src = os.path.join(tmpdir, "input.png")
        dst = os.path.join(tmpdir, "output.png")
        img.save(src)

        crop_to_square(src, dst)

        result = Image.open(dst)
        assert result.size[0] == result.size[1] == 100


def test_add_background():
    from designs.utils.transparent_to_color import add_background

    with tempfile.TemporaryDirectory() as tmpdir:
        img = Image.new("RGBA", (50, 50), (255, 0, 0, 128))
        src = os.path.join(tmpdir, "input.png")
        dst = os.path.join(tmpdir, "output.png")
        img.save(src)

        add_background(src, (0, 0, 0, 255), dst)

        result = Image.open(dst)
        assert result.mode == "RGB"
        assert result.size == (50, 50)


def test_colormaps_plot():
    from designs.utils.colormaps_mpl import plot_color_gradients

    fig = plot_color_gradients("Test", ["viridis", "plasma"])
    assert fig is not None
    assert len(fig.axes) == 2


def test_designs_structure():
    expected_dirs = [
        "designs/fractals",
        "designs/differential_equations",
        "designs/geometric_patterns",
        "designs/heatmaps",
        "designs/random_walks",
        "designs/particle_simulations",
        "designs/curves",
        "designs/utils",
    ]
    base = os.path.dirname(os.path.dirname(__file__))
    for d in expected_dirs:
        path = os.path.join(base, d)
        assert os.path.isdir(path), f"Missing directory: {d}"
