import datetime
import logging
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np

from sat_data.services.utils.dataset_utils import get_dataset
from sat_data.models import SatData, Band
from sat_data.enums.sat_band import SatBand
from sat_data.enums.idx_img_type import IdxImgType

logger = logging.getLogger("django")

class MetricsCalculator:
    """
    MetricsCalculator is a basis class for calculating metrics on satellite images.
    """

    @staticmethod
    def create_plot_img(nested_array, save_loc, cmap="", interpolation=""):
        """
        Creates an image with MatPlotLib and saves it to desired save location.
        """
        logger.info(
            f"Creating plot image. save_location='{save_loc}', cmap='{cmap}', interpolation='{interpolation}'")
        try:
            mpl.use("agg")
            if cmap != "" and interpolation != "":
                plt.imshow(nested_array, cmap=cmap, interpolation=interpolation)
            elif cmap != "" and interpolation == "":
                plt.imshow(nested_array, cmap=cmap)
            elif cmap == "" and interpolation != "":
                plt.imshow(nested_array, interpolation=interpolation)
            elif cmap == "" and interpolation == "":
                plt.imshow(nested_array)

            # plt.colorbar()
            plt.axis('off')
            plt.savefig(save_loc, dpi=200,
                        bbox_inches='tight', pad_inches=0.0)
            plt.close('all')
        except Exception as e:
            logger.error(f"Failed to save image. save_location='{save_loc}', cmap='{cmap}', interpolation='{interpolation}'")
            return False

        logger.info(f"Successfully saved image. save_location='{save_loc}', cmap='{cmap}', interpolation='{interpolation}'")
        return True

    @staticmethod
    def calculate_evi(sat_data: SatData, g: int = 1, c1: int = 2.5,
                      c2: int = 2.5, l: int = 1):
        """
        Calculates the EVI (Enhanced Vegetation Index) which is similar to the NDVI but more sensitive in high biomass regions.

        For the Sentinel-2 image data we are using G=1, C1=2.5, C2=2.5 and L=1.

        :param sat_data:
        :param image_path_02:
        :param image_path_04:
        :param image_path_8a:
        :param save_location:
        :param g: G is a gain factor.
        :param c1: C1, C2 are the coefficients of the aerosol resistance term, which uses the blue band to correct for aerosol influences in the red band.
        :param c2: Same as C1.
        :param l: L is the canopy background adjustment that addresses non-linear, differential NIR and red radiant transfer through a canopy.
        """
        # Get band info and image save location
        band_info: Band = sat_data.get_band(
            SatBand.B02.value,
            SatBand.B04.value,
            SatBand.B8A.value
        )
        save_loc = sat_data.img_save_loc(IdxImgType.EVI.value)

        # Read datasets
        dataset_b02 = get_dataset(band_info.b02_path)  # BLUE
        dataset_b04 = get_dataset(band_info.b04_path)  # RED
        dataset_b8a = get_dataset(band_info.b8a_path)  # NIR

        blue_band_b02 = dataset_b02.read(1).astype(float)
        red_band_b04 = dataset_b04.read(1).astype(float)
        nir_band_b8a = dataset_b8a.read(1).astype(float)

        logger.debug(
            f"Read blue (BLUE), red (RED) and near-infrared (NIR) from dataset for EVI calculation. sat_data_id='{sat_data.id}'")
        logger.debug(
            f"Using the variables G='{g}', C1='{c1}', C2='{c2}', L='{l}' for EVI calculation. sat_data_id='{sat_data.id}'")

        # Calculation
        evi = [0]
        try:
            evi = g * ((nir_band_b8a - red_band_b04) / (nir_band_b8a +
                       c1 * red_band_b04 - c2 * blue_band_b02 + l))
        except RuntimeWarning:
            logger.warning(
                f"Invalid value found during division of the enhanced vegetation index (EVI). sat_data_id='{sat_data.id}'")
            logger.info(
                f"EVI Calculation will be continued... sat_data_id='{sat_data.id}'")

        logger.info(f"Calculated EVI. sat_data_id='{sat_data.id}'")

        # Create and save image
        cmap = "RdYlGn"
        datetime_formatted = datetime.datetime.now() \
            .strftime("%Y%m%d_%H%M%S")  # "20231231_235959"
        save_loc = f"{save_loc}/{sat_data.id}_evi_{datetime_formatted}.png"

        ok = MetricsCalculator.create_plot_img(
            nested_array=evi,
            cmap=cmap,
            save_loc=save_loc
        )
        if not ok:
            logger.error(f"Failed to save EVI image. sat_data_id='{sat_data.id}', save_loc='{save_loc}'")
            return ""

        logger.debug(
            f"Saved EVI image '{save_loc} with cmap '{cmap}'. save_loc='{save_loc}', sat_data_id='{sat_data.id}'")
        return save_loc

    @staticmethod
    def calculate_ndwi(sat_data: SatData) -> str:
        """
        Calculates the NDWI (Normalized Difference Water Index) which is used to monitor changes in water content of vegetation's leaves.

        :param sat_data:
        :param image_path_03:
        :param image_path_08:
        """
        # Get band info and image save location
        band_info: Band = sat_data.get_band(
            SatBand.B03.value,
            SatBand.B08.value,
        )
        save_loc = sat_data.img_save_loc(IdxImgType.NDWI.value)

        # Read datasets
        dataset_b03 = get_dataset(band_info.b03_path)  # GREEN
        dataset_b08 = get_dataset(band_info.b08_path)  # VNIR

        vnir_band_b08 = dataset_b08.read(1).astype(float)
        green_band_b03 = dataset_b03.read(1).astype(float)
        logger.debug(
            f"Read near-infrared (VNIR) and green (GREEN) from dataset. sat_data_id='{sat_data.id}'")

        # Calculation
        ndwi = [0]
        try:
            ndwi = (green_band_b03 - vnir_band_b08) / \
                (green_band_b03 + vnir_band_b08)
        except RuntimeWarning as e:
            logger.warning(
                f"Invalid value found during division of the enhanced vegetation index (EVI). error='{e}', sat_data_id='{sat_data.id}'")

        logger.info(f"Calculated NDWI. sat_data_id='{sat_data.id}'")

        # Create and save image
        cmap = "winter"
        datetime_formatted = datetime.datetime.now() \
            .strftime("%Y%m%d_%H%M%S")  # "20231231_235959"
        save_loc = f"{save_loc}/{sat_data.id}_ndwi_{datetime_formatted}.png"

        ok = MetricsCalculator.create_plot_img(
            nested_array=ndwi,
            cmap=cmap,
            save_loc=save_loc
        )
        if not ok:
            logger.error(f"Failed to save NDWI image. sat_data_id='{sat_data.id}', save_loc='{save_loc}'")
            return ""

        logger.info(
            f"Saved NDWI image '{save_loc} with cmap '{cmap}' under location '{save_loc}'. sat_data_id='{sat_data.id}'")
        return save_loc

    @staticmethod
    def calculate_ndvi(sid_id, image_path_04, image_path_08, save_location="") -> str:
        """
        Calculates the Normalized Difference Vegetation Index (NDVI).
        The NDVI is an indicator of the greenness of the biomes.

        :param sid_id:
        :param save_location:
        :param image_path_8:
        :param image_path_04:
        """
        # TODO: get average float ndvi and return it
        # Load dataset from band 04 + 8
        dataset_04 = get_dataset(image_path_04)
        dataset_8 = get_dataset(image_path_08)

        # Calculate NIR and RED bands
        vnir_band_08 = dataset_8.read(1).astype(float)
        red_band_04 = dataset_04.read(1).astype(float)
        logger.debug(
            f"Read near-infrared (VNIR/band 08) and red (RED/band 04) from dataset. sat_data_id='{sat_data.id}'")

        # Calculate NDVI
        ndvi = [0]
        try:
            ndvi = (vnir_band_08 - red_band_04) / (vnir_band_08 + red_band_04)
        except RuntimeWarning as e:
            logger.warning(
                f"Invalid value found during division of the normalized difference vegetation index (NDVI). error='{e}', sat_data_id='{sat_data.id}'")

        logger.info(f"Calculated NDVI. sat_data_id='{sat_data.id}'")

        # Saving/displaying NDVI map
        cmap = "RdYlGn"
        datetime_formatted = datetime.datetime.now().strftime(
            "%Y%m%d_%H%M%S")  # "20231231_235959"
        save_location = f"{save_location}/{sat_data.id}_ndvi_{datetime_formatted}.png"
        MetricsCalculator.create_plot_img(
            nested_array=ndvi,
            cmap=cmap,
            save_loc=save_location
        )
        logger.info(
            f"Saved NDVI image '{save_location} with cmap '{cmap}' under location '{save_location}'. sat_data_id='{sat_data.id}'")
        return save_location

    @staticmethod
    def calculate_moisture(sid_id, image_path_8a, image_path_11, save_location="") -> str:
        """
        The moisture index shows how wet the soil is.

        :param sid_id:
        :param image_path_8a:
        :param image_path_11:
        :param save_location:
        :return:
        """
        # Load dataset from band 8a + 12
        dataset_8a = get_dataset(image_path_8a)
        dataset_11 = get_dataset(image_path_11)

        # Calculate SWIR and RED bands
        vnir_band_8a = dataset_8a.read(1).astype(float)
        swir_band_11 = dataset_11.read(1).astype(float)
        logger.debug(
            f"Read visible and near infrared (VNIR/band 8a) and short-wave infrared (SWIR/band 11). id='{sat_data.id}'")

        # Calculate moisture index
        moisture_index = [0]
        try:
            moisture_index = (vnir_band_8a - swir_band_11) / \
                (vnir_band_8a + swir_band_11)
        except RuntimeWarning as e:
            logger.warning(
                f"Invalid value found during division of the moisture index. error='{e}', sat_data_id='{sat_data.id}'")

        logger.info(
            f"Calculated moisture index. sat_data_id='{sat_data.id}'")

        # Saving/displaying moisture index map
        cmap = "Blues"
        datetime_formatted = datetime.datetime.now().strftime(
            "%Y%m%d_%H%M%S")  # "20231231_235959"
        save_location = f"{save_location}/{sat_data.id}_moisture_index_{datetime_formatted}.png"
        MetricsCalculator.create_plot_img(
            nested_array=moisture_index,
            cmap=cmap,
            save_loc=save_location
        )
        logger.info(
            f"Saved moisture index image '{save_location} with cmap '{cmap}' under location '{save_location}'. sat_data_id='{sat_data.id}'")
        return save_location

    @staticmethod
    def calculate_ndsi(sid_id, image_path_03, image_path_11, save_location="") -> str:
        """
        Calculates the NSDI (Normalized Difference Snow Index) which is used to seperate snow from vegetation, soils and lthology endmembers.

        :param sid_id:
        :param image_path_03:
        :param image_path_11:
        :param save_location:
        """
        dataset_03 = get_dataset(image_path_03)  # GREEN
        dataset_11 = get_dataset(image_path_11)  # SWIR

        green_band_03 = dataset_03.read(1).astype(float)
        swir_band_11 = dataset_11.read(1).astype(float)
        logger.debug(
            f"Read green (GREEN/band 03) and near-infrared (SWIR/band 11) from dataset. sat_data_id='{sat_data.id}'")

        ndsi = [0]
        try:
            ndsi = (green_band_03 - swir_band_11) / \
                (green_band_03 + swir_band_11)
        except RuntimeWarning as e:
            logger.warning(
                f"Invalid value found during division of the normalized difference snow index index (NDSI). error='{e}', sat_data_id='{sat_data.id}'")

        logger.info(f"Calculated NDSI. sat_data_id='{sat_data.id}'")

        interpolation = "lanczos"
        datetime_formatted = datetime.datetime.now().strftime(
            "%Y%m%d_%H%M%S")  # "20231231_235959"
        save_location = f"{save_location}/{sat_data.id}_ndsi_{datetime_formatted}.png"

        MetricsCalculator.create_plot_img(
            nested_array=ndsi,
            save_loc=save_location,
            interpolation=interpolation,
        )
        logger.info(
            f"Saved NDSI image '{save_location} with interpolation '{interpolation}' under location '{save_location}'. sat_data_id='{sat_data.id}'")
        return save_location

    @staticmethod
    def create_rgb_img(sid_id, blue_band_02, green_band_03, red_band_04, save_location=""):
        """
        Creates a RGB image from the satellite bands blue (band 02), green (band 03) and red (band 04).

        :param sid_id:
        :param blue_band_02:
        :param green_band_03:
        :param red_band_04:
        :param save_location:
        :return:
        """
        # Read image and create dataset
        band_02 = get_dataset(blue_band_02)
        band_03 = get_dataset(green_band_03)
        band_04 = get_dataset(red_band_04)

        # Read band from dataset
        red = band_04.read(1)
        green = band_03.read(1)
        blue = band_02.read(1)

        # Brighten
        red_b = MetricsCalculator.__brighten(red)
        blue_b = MetricsCalculator.__brighten(blue)
        green_b = MetricsCalculator.__brighten(green)

        # Gamma Correction
        red_g = MetricsCalculator.__gamma_correction(red_b)
        blue_g = MetricsCalculator.__gamma_correction(blue_b)
        green_g = MetricsCalculator.__gamma_correction(green_b)

        # Normalize
        red_bn = MetricsCalculator.__normalize(red_g)
        green_bn = MetricsCalculator.__normalize(green_g)
        blue_bn = MetricsCalculator.__normalize(blue_g)

        # Stack up the bands
        rgb_composite = np.dstack((red_bn, green_bn, blue_bn))

        # Save location path
        datetime_formatted = datetime.datetime.now().strftime(
            "%Y%m%d_%H%M%S")  # "20231231_235959"
        save_location = f"{save_location}/{sat_data.id}_rgb_{datetime_formatted}.png"

        # Save as .png
        interpolation = 'lanczos'
        MetricsCalculator.create_plot_img(
            nested_array=rgb_composite,
            interpolation=interpolation,
            save_loc=save_location)
        # plt.imshow(rgb_composite)
        # plt.axis('off'),
        # plt.savefig(save_location, dpi=200, bbox_inches='tight', pad_inches=0.0)
        # plt.close('all')

        return save_location

    @staticmethod
    def __normalize(band):
        band_min, band_max = (band.min(), band.max())
        return (band - band_min) / (band_max - band_min)

    @staticmethod
    def __brighten(band):
        alpha = 0.13
        beta = 0
        return np.clip(alpha * band + beta, 0, 255)

    @staticmethod
    def __gamma_correction(band):
        gamma = 2
        return np.power(band, 1 / gamma)
