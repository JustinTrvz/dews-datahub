import logging
from tkinter import Image


class ImageUtils():
    """ Image utils for TIFF, PNG, ..."""


    def tiff_to_png(tiff_path: str, png_path: str) -> str:
        """
        Converts TIFF file to PNG.
        
        Takes TIFF file from `tiff_path`  and saves the PNG to `png_path`.
        """
        try:
            tiff_image = Image.open(tiff_path)
            tiff_image.save(png_path, format="PNG")
            logging.debug(f"TIFF to PNG conversion successful. tiff_path='{tiff_path}', png_path='{png_path}'")
        except Exception as e:
            logging.error(f"Error occurred while converting a TIFF to PNG. tiff_path='{tiff_path}', png_path='{png_path}' error='{e}' ")