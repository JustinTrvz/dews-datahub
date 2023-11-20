import logging

import rasterio


class DatasetUtils:
    """
    Loads dataset using Rasterio package.
    """

    @staticmethod
    def get_dataset(image_path):
        try:
            dataset = rasterio.open(image_path)
        except Exception as e:
            logging.error(f"Could not open dataset. error='{e}', image_path='{image_path}'")
            return
        logging.debug(f"Returning dataset. image_path='{image_path}'")
        return dataset

    """
    Returns information about width, height, bands, crs and transform of loaded dataset.
    """

    @staticmethod
    def get_dataset_infos(dataset):
        width = dataset.width
        height = dataset.height
        count = dataset.count
        crs = dataset.crs
        transform = dataset.transform

        dataset_info_string = f"Width: {dataset.width}, Height: {height}, Count: {count}, CRS: {crs}, Transform: {transform}"

        logging.debug(f"Return dataset info. dataset: {dataset}, dataset_info_string: {dataset_info_string}")
        return width, height, count, crs, transform

    """
    Loads specific band from dataset.
    """

    @staticmethod
    def load_band(image_path, band_number):
        dataset = DatasetUtils.get_dataset(image_path)
        width, height, bands, crs, transform = DatasetUtils.get_dataset_infos(dataset)

        logging.debug(f"Returned band. band_number='{band_number}', image_path='{image_path}'.")

        return dataset.read(band_number)
