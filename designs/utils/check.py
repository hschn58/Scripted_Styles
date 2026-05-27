import os

def unique_filename(filepath):
    """
    If 'filepath' already exists, append '1' before the extension.
    Otherwise return 'filepath' unchanged.
    """
    while True:
        if os.path.exists(filepath):
            root, ext = os.path.splitext(filepath)
            # e.g. if filepath == "/path/collage2.png",
            # then root == "/path/collage2", ext == ".png"
            filepath = root + "1" + ext
        else:
            return filepath
        
