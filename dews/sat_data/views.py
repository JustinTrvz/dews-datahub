
from concurrent.futures import ThreadPoolExecutor
import logging
import os
from threading import Thread
import uuid
from requests import HTTPError
from sentinelhub import MimeType, DataCollection
from datetime import datetime, timedelta, date
import json
from PIL import Image

from django.contrib.gis.geos import Polygon, GEOSGeometry

from django.core.serializers import serialize
from django.http import HttpResponseBadRequest, JsonResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.views.decorators.http import require_POST

from sat_data.enums.sat_mission import SatMission
from sat_data.enums.status import Status
from sat_data.services.utils.file_utils import FileUtils
from sat_data.models import SHRequest, SatData, TimeTravel, remove_media_root
from sat_data.forms import SHRequestForm, SatDataForm
from sat_data.services.attr_adder import AttrAdder
from sat_data.services.metrics_calc import MetricsCalculator
from sat_data.services.sentinel_hub import request_sat_data
from dews.settings import MEDIA_ROOT, VERSION, ARCHIVE_FILES_PATH
from django.db import connection
import shutil
from werkzeug.utils import secure_filename

logger = logging.getLogger("django")


def time_travel_details_view(request, time_travel_id):
    if not request.user.is_authenticated:
        logger.debug(
            f"User '{request.user}' is not authenticated to see TimeTravel details page of '{time_travel_id}'.")
        return redirect("login_view")

    # Get time travel obj
    time_travel: TimeTravel = get_object_or_404(TimeTravel, id=time_travel_id)

    context = {
        "version": VERSION,
        "time_travel": time_travel,
        "time_travel_geojson": None,
    }

    # Create GeoJSON
    if time_travel.coordinates:
        context["time_travel_geojson"] = serialize(
            "geojson", [time_travel], geometry_field="leaflet_coordinates", fields=())
    else:
        context["time_travel_geojson"] = None

    return render(request, "time_travel_details_view.html", context)


def time_travel_delete_view(request, time_travel_id):
    if not request.user.is_authenticated:
        logger.debug(
            f"User '{request.user}' is not authenticated to delete TimeTravel object '{time_travel_id}'.")
        return redirect("login_view")

    # Get time travel obj
    time_travel: TimeTravel = get_object_or_404(TimeTravel, id=time_travel_id)

    # Check if the time_travel object is associated with any sat_data objects
    if hasattr(time_travel, "satdata"):
        # Delete associated sat data objects
        for sat_data in time_travel.satdata.all():
            sat_data.delete()
            logger.info(
                f"Deleted associated SatData object '{sat_data.id}'. time_travel_id='{time_travel_id}' user='{request.user}'")

    # Delete time travel obj
    time_travel.delete()
    logger.info(
        f"Deleted TimeTravel object '{time_travel_id}'. user='{request.user}'")

    return redirect("overview_view")


def sat_data_details_view(request, sat_data_id):
    if not request.user.is_authenticated:
        logger.debug(
            f"User '{request.user}' is not authenticated to see SatData details page of '{sat_data_id}'.")
        return redirect("login_view")

    # Get sat data obj
    sat_data: SatData = get_object_or_404(SatData, id=sat_data_id)

    context = {
        "version": VERSION,
        "sat_data": sat_data,
        "sat_data_geojson": None,
        "title": sat_data.name,
    }

    # Create GeoJSON
    if sat_data.coordinates:
        context["sat_data_geojson"] = serialize(
            'geojson', [sat_data], geometry_field='leaflet_coordinates', fields=())
    else:
        context["sat_data_geojson"] = None

    return render(request, "sat_data_details_view.html", context)


def sat_data_delete_view(request, sat_data_id):
    if not request.user.is_authenticated:
        logger.debug(
            f"User '{request.user}' is not authenticated to delete SatData object '{sat_data_id}'.")
        return redirect("login_view")

    # Get sat data obj
    sat_data: SatData = get_object_or_404(SatData, id=sat_data_id)

    # Check if user is owner
    if sat_data.user != request.user:
        logger.debug(
            f"User '{request.user}' is not owner of SatData object '{sat_data_id}'.")
        return redirect("dashboard_view")

    # Delete sat data obj
    # Get the `band_tables` from the sat_data object
    if hasattr(sat_data, "band_tables") and sat_data.band_tables is not None:
        band_tables = sat_data.band_tables

        # Iterate over each resolution in the `band_tables`
        for _, tables in band_tables.items():
            # Iterate over each table in the resolution
            for table in tables:
                # Create the SQL statement to drop the table
                sql = f'DROP TABLE IF EXISTS "{table}";'
                # Execute the SQL statement
                with connection.cursor() as cursor:
                    cursor.execute(sql)
                logging.debug(
                    f"Deleted table '{table}' from database. user='{request.user}', sat_data_id='{sat_data_id}'")

    # # Check if the sat_data object is associated with any time_travel objects
    # if hasattr(sat_data, "time_travels"):
    #     # Check if the time_travel object only has this sat_data instance
    #     time_travel = sat_data.time_travels
    #     if time_travel.satdata.count() == 1:
    #         # Delete the time_travel object
    #         time_travel.delete()
    #         logger.info(
    #             f"Deleted TimeTravel object '{time_travel.id}' associated with SatData object '{sat_data_id}'. user='{request.user}'")

    sat_data.delete()
    logger.info(
        f"Deleted SatData object '{sat_data_id}'. user='{request.user}'")

    return redirect("overview_view")


def overview_view(request):
    if not request.user.is_authenticated:
        logger.debug(
            f"User '{request.user}' is not authenticated to see overview.")
        return redirect("login_view")

    # Start with all entries
    sat_data_entries = SatData.objects.all()
    time_travel_entries = TimeTravel.objects.all()

    # Filter by search query if it exists
    search_query = request.GET.get('search', '')
    if search_query:
        sat_data_entries = sat_data_entries.filter(
            name__icontains=search_query)
        time_travel_entries = time_travel_entries.filter(
            name__icontains=search_query)

    # Filter by mission if it exists
    mission_query = request.GET.get('mission', '')
    if mission_query:
        sat_data_entries = sat_data_entries.filter(mission=mission_query)
        time_travel_entries = time_travel_entries.filter(mission=mission_query)

    # Filter by product type if it exists
    prod_type_query = request.GET.get('product_type', '')
    if prod_type_query:
        sat_data_entries = sat_data_entries.filter(
            product_type=prod_type_query)
        time_travel_entries = time_travel_entries.filter(
            product_type=prod_type_query)

    logger.debug(
        f"Search query: '{search_query}', Mission query: '{mission_query}', Product type query: '{prod_type_query}'")

    context = {
        "version": VERSION,
        "sat_data_entries": sat_data_entries,
        "sat_data_entries_count": sat_data_entries.count(),
        "time_travel_entries": time_travel_entries,
        "time_travel_entries_count": time_travel_entries.count(),
        "search_query": search_query,
        "mission_query": mission_query,
        "prod_type_query": prod_type_query,
    }
    return render(request, "overview_view.html", context)


def sat_data_create_view(request):
    # Check user
    if not request.user.is_authenticated:
        logger.debug(
            f"User '{request.user}' is not authenticated to upload files.")
        return redirect("dashboard_view")

    logger.debug(f"request='{request}'")
    logger.debug(f"request.user='{request.user}'")
    logger.debug(f"request.method='{request.method}'")
    logger.debug(f"request.POST='{request.POST}'")
    logger.debug(f"request.FILES='{request.FILES}'")

    context = {
        "version": VERSION,
        "error": None,  # will be overwritten, if needed
        "success": None,  # will be overwritten, if needed
        "sat_data_form": SatDataForm(request.POST or None, request.FILES or None),
        "sh_form": SHRequestForm(request.POST or None, request.FILES or None),
        "sat_data_id": None,
    }

    # POST request -> create SatData obj
    if request.method == "POST":
        logger.debug(f"POST request.")
        if "sat_data_button" in request.POST:
            logger.debug(f"'SatData' button clicked.")
            # SatDataForm
            archive = request.FILES.get("archive")

            # Check user input
            if not archive:
                return HttpResponseBadRequest("Archive file is required.")

            # Validate and sanitize the filename
            filename = secure_filename(archive.name)

            # Write archive to file system
            archive_path = ARCHIVE_FILES_PATH / filename
            if not os.path.exists(archive_path):
                # Archive does not exist
                logger.info(
                    f"Archive does not exist. Will write archive to file system. archive_path='{archive_path}'")
                try:
                    with open(archive_path, "wb+") as file_ref:
                        logger.info(f"Writing archive to file system. archive_path='{archive_path}'")
                        for chunk in archive.chunks():
                            file_ref.write(chunk)
                    logger.info(
                        f"Done writing archive to file system. archive_path='{archive_path}'")
                except Exception as e:
                    logger.error(
                        f"Failed to write archive to file system. archive_path='{archive_path}', error='{e}'")
            else:
                # Archive already exists
                logger.info(
                    f"Archive already exists. archive_path='{archive_path}'")

            # Extract and create SatData obj
            try:
                sat_data_id = create_sat_data(request, archive_path)
                if sat_data_id is None:
                    raise Exception(
                        f"Failed to create SatData object. sat_data_id='{sat_data_id}'")
            except Exception as e:
                # Background task failed
                logger.error(
                    f"Failed 'extract_and_create' background task. username='{request.user.username}', error='{e}'")
                err_msg = "Failed to extract and create archive. However, an entry was still created."
                context["error"] = err_msg
                logger.debug(
                    f"Render 'sat_data_create_view.html' with error message: '{err_msg}'.")
                return render(request, "sat_data_create_view.html", context)

            # Upload done
            success_msg = f"Upload done! Work in progress... archive='{filename}'"
            context["success"] = success_msg
            logger.debug(
                f"Render 'sat_data_create_view.html' with success message: '{success_msg}'.")
            return render(request, "sat_data_create_view.html", context)
        elif "sh_button" in request.POST:
            logger.debug(f"'SentinelHub' button clicked.")
            # SHRequestForm
            return sentinel_hub_request_view(request, context)

    # GET request -> view and form
    logger.debug("Render 'sat_data_create_view.html'.")
    return render(request, "sat_data_create_view.html", context)


def create_sat_data(request, archive_path) -> bool:
    logger.debug(f"Create background task.")
    logger.info(
        f"Extract and create SatData obj. username='{request.user.username}', archive_path='{archive_path}'")
    try:
        # Start background task
        thread = Thread(target=__extract_and_create,
                        args=(request, str(archive_path), logger))
        thread.start()
        logger.debug(
            f"Started 'extract_and_create' background task. username='{request.user.username}', archive_path='{archive_path}'")
    except Exception as e:
        # Background task failed
        logger.error(
            f"Failed to start 'extract_and_create' background task. username='{request.user.username}', error='{e}'")
        return False

    return True


def __extract_and_create(request, archive_path: str, logger: logging.Logger = None):
    # Extract archive
    logger.info(f"Extracting archive. archive_path='{archive_path}'")
    mission = SatMission.get_mission_by_filename(archive_path)
    # Check if extracted directory exists
    extracted_path = FileUtils.extract_archive(archive_path, mission)
    logger.debug(f"Extracted path='{extracted_path}'")
    if extracted_path is None or extracted_path == "":
        logger.error(
            f"Extracting archive failed... extracted_path='{extracted_path}'")
        return

    # Create SatData object
    logger.info(
        f"Creating SatData object. username='{request.user.username}', extracted_path='{extracted_path}'")
    form = SatDataForm(request.POST or None, request.FILES or None)
    # Check form
    if form.is_valid():
        logger.debug(f"Form is valid. form='{form}'")
        try:
            # Save SatData object to database
            sat_data: SatData = form.save(commit=False)
            sat_data.id = uuid.uuid4()
            sat_data.user = request.user
            logger.debug(
                f"Created form, added id and user. id='{sat_data.id}'")

            # Add paths
            sat_data.archive = remove_media_root(archive_path)
            logger.debug(f"Added archive file. sat_data.id='{sat_data.id}'")
            sat_data.extracted_path = remove_media_root(extracted_path)
            logger.debug(f"Added extracted path. sat_data.id='{sat_data.id}'")

            # Add attributes (like mission, product type, band img paths, ...)
            logger.debug(
                f"Calling AttrAdder. sat_data.id='{sat_data.id}', extracted_path='{extracted_path}', mission='{mission}', product_type='{sat_data.product_type}'")
            attr_adder = AttrAdder(
                sat_data=sat_data,
                extracted_path=extracted_path,
                mission=mission)
            attr_adder.start()
            logger.info(
                f"Created SatData with several attributes. id='{sat_data.id}', extracted_path='{extracted_path}'")
            sat_data.save()

            # Calculate metrics
            metrics_to_calc = ["ndvi", "rgb"]
            if metrics_to_calc:
                logger.debug(
                    f"Calling MetricsCalculator. sat_data.id='{sat_data.id}', extracted_path='{extracted_path}', mission='{mission}', product_type='{sat_data.product_type}'")
                mc = MetricsCalculator(
                    sat_data=sat_data,
                    metrics_to_calc=metrics_to_calc)
                mc.start()
                logger.info(
                    f"Metrics calculation done. metrics_to_calc='{metrics_to_calc}', sat_data.id='{sat_data.id}'")
            else:
                logger.info(
                    f"No metrics to calculate. sat_data.id='{sat_data.id}'")

            return
        except Exception as e:
            # Save failed
            logger.error(
                f"Failed to create, add attributes and save a SatData object. username='{request.user.username}', extracted_path='{extracted_path}', error='{e}'")
            return
    else:
        # Form is not valid
        logger.error(
            f"Form is not valid. username='{request.user.username}', extracted_path='{extracted_path}', form='{form}'")
        return


def create_sh_sat_data(request, data_folder, dir_name, bbox, bands, metrics_to_calc: list, date) -> str:
    """

    :return: SatData object on success; None on failure
    """
    logger.info(
        f"Creating SatData object. username='{request.user.username}', path='{data_folder}/{dir_name}'")
    # Create form
    form = SatDataForm(request.POST or None, request.FILES or None)
    try:
        # Create SatData object
        sat_data: SatData = form.save(commit=False)
        sat_data.id = uuid.uuid4()
        sat_data.user = request.user
        logger.debug(
            f"Created form, added id and user. id='{sat_data.id}'")

        # Add paths
        extracted_path = remove_media_root(os.path.join(data_folder, dir_name))
        logger.debug(f"Added extracted path. sat_data.id='{sat_data.id}'")

        # Add attributes (like mission, product type, band img paths, ...)
        logger.debug(
            f"Calling AttrAdder. sat_data.id='{sat_data.id}', extracted_path='{extracted_path}'")
        attr_adder = AttrAdder(
            sat_data=sat_data,
            extracted_path=extracted_path,
            mission=SatMission.SENTINEL_2B.value,
            sh_request=True,
            bbox=bbox,
            bands=bands,
            date=date
        )
        attr_adder.start()
        logger.info(
            f"Created SatData with several attributes. id='{sat_data.id}', extracted_path='{extracted_path}'")

        # Calculate metrics
        logger.debug(
            f"Calling MetricsCalculator. sat_data.id='{sat_data.id}', extracted_path='{extracted_path}', sat_data.mission='{sat_data.mission}', sat_data.product_type='{sat_data.product_type}'")
        if metrics_to_calc:
            mc = MetricsCalculator(
                sat_data=sat_data,
                metrics_to_calc=metrics_to_calc)
            mc.start()
            logger.info(
                f"Metrics calculation done. metrics_to_calc='{metrics_to_calc}', sat_data.id='{sat_data.id}'")
        else:
            logger.info(
                f"No metrics to calculate. sat_data.id='{sat_data.id}'")

        return sat_data
    except Exception as e:
        logger.error(
            f"Failed to create SatData object from Sentinel Hub request. user='{request.user}', error='{e}'")
        return None

def is_uniform_color(image_path):
    with Image.open(image_path) as img:
        pixels = list(img.getdata())
        first_pixel = pixels[0]
        
        # Check if all pixels are the same as the first one
        for pixel in pixels[1:]:
            if pixel != first_pixel:
                return False
        return True

@require_POST
def sentinel_hub_request_view(request, context):
    logger.debug(f"request='{request}'")
    logger.debug(f"request.user='{request.user}'")
    logger.debug(f"request.method='{request.method}'")
    logger.debug(f"request.POST='{request.POST}'")

    form = SHRequestForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        logger.debug("SHRequestForm is valid.")
        logger.debug("Sentinel Hub Request request: ", request)
        data = form.cleaned_data
        logger.debug("Sentinel Hub Request JSON: ", data)

        mission = data.get('mission')  # str
        metrics_to_calc = data.get('metrics_to_calc', [])
        bands = data.get('bands', ["B02", "B03", "B04"])
        start_date = data.get('start_date')  # datetime
        end_date = data.get('end_date', start_date)  # datetime
        resolution = data.get('resolution', 60)  # int: 10m, 20m or 60m per pixel
        coordinates = data.get('coordinates')  # Polygon
        data_folder = f"{MEDIA_ROOT}/sentinel_hub"

        # Debug all input values
        logger.debug(f"SHRequest - Mission: {mission}")
        logger.debug(f"SHRequest - Metrics to calculate: {metrics_to_calc}")
        logger.debug(f"SHRequest - Bands: {bands}")
        logger.debug(f"SHRequest - Start date: {start_date}")
        logger.debug(f"SHRequest - End date: {end_date}")
        logger.debug(f"SHRequest - Resolution: {resolution}")
        logger.debug(f"SHRequest - Coordinates: {coordinates}")
        logger.debug(f"SHRequest - Data folder: {data_folder}")

        # Check start date
        if datetime(start_date.year, start_date.month, start_date.day) >= datetime.today():
            # Start date can not be today or in the future
            err_msg = "Start date is today or in the future. Please choose a start date that is in the past."
            logger.debug(f"{err_msg} start_date='{start_date}', end_date='{end_date}', mission='{mission}', bands='{bands}', resolution='{resolution}'")
            context["error"] = err_msg
            return render(request, "sat_data_create_view.html", context)
        # Check end date
        if datetime(end_date.year, end_date.month, end_date.day) >= datetime.today():
            # End date can not be today or in the future
            err_msg = "End date is today or in the future. Please choose a end date that is in the past."
            logger.debug(f"{err_msg} start_date='{start_date}', end_date='{end_date}', mission='{mission}', bands='{bands}', resolution='{resolution}'")
            context["error"] = err_msg
            return render(request, "sat_data_create_view.html", context)

        if coordinates:
            # Create SHRequest object
            sh_request: SHRequest = form.save(commit=False)
            sh_request.id = uuid.uuid4()
            sh_request.user = request.user
            sh_request.save()

            # Create tuple
            if isinstance(coordinates, str):
                bbox = tuple(float(coordinate)
                             for coordinate in coordinates.split(','))
            elif isinstance(coordinates, Polygon):
                bbox = wkt_to_coordinates_str(coordinates)

            # Set data collection
            if mission == "SENTINEL2_L1C":
                data_collection = DataCollection.SENTINEL2_L1C
            else:
                data_collection = DataCollection.SENTINEL2_L2A
            mission = SatMission.SENTINEL_2B

            # Create SHRequest and SatData object
            try:
                # Request SatData
                response = request_sat_data(
                    bbox=bbox,
                    resolution=int(resolution),
                    data_folder=data_folder,
                    data_collection=data_collection,
                    mimetypes=[MimeType.TIFF, MimeType.PNG],
                    bands=bands,
                    start_date=start_date,
                    end_date=end_date,
                )
                logger.debug(
                    f"Requesting Sentinel Hub data done. bbox='{bbox}', resolution='{resolution}', data_folder='{data_folder}', data_collection='{data_collection}', bands='{bands}'")

                dir_name = response.get_filename_list()[0].split('/')[0]

                # Check if response image is valid
                dir_path = FileUtils.generate_path(data_folder, dir_name)
                tar_path = FileUtils.generate_path(dir_path, "response.tar")
                extracted_path = FileUtils.extract_tar(tar_path)
                png_path = FileUtils.generate_path(extracted_path, "default.png")

                if is_uniform_color(png_path):
                    # Retry request
                    logger.warn(
                        f"Failed request. Uniform color image detected. start_date='{start_date}', end_date='{end_date}', bbox='{bbox}', band='{bands}', resolution='{resolution}'")
                    # Delete downloaded directory 
                    shutil.rmtree(dir_path)
                    success_request = False
                else:
                    logger.debug(f"Successfull Sentinel Hub request. Non-uniform color image detected. start_date='{start_date}', end_date='{end_date}', bbox='{bbox}', band='{bands}', resolution='{resolution}'")
                    success_request = True

                # Error: max retries reached, no successfull request
                if not success_request:
                    err_msg = f"Failed request. No data available for this date range: '{start_date}'-'{end_date}'."
                    logger.warn(f"{err_msg} start_date='{start_date}', end_date='{end_date}', bbox='{bbox}', bands='{bands}', resolution='{resolution}'")
                    context["error"] = f"{err_msg} Please try again with a different date range."
                    return render(request, "sat_data_create_view.html", context)

                # Create SatData object
                logger.debug(
                    f"Create SatData object from Sentinel Hub request. user='{request.user}', dir_name='{dir_name}', bbox='{bbox}', timestamp='{datetime.now()}'")
                sat_data: SatData = create_sh_sat_data(
                    request=request,
                    data_folder=data_folder,
                    dir_name=dir_name,
                    bbox=bbox,
                    bands=bands,
                    metrics_to_calc=metrics_to_calc,
                    date=end_date,
                )

                # Check SatData object
                if not sat_data:
                    # Error: SatData object not created
                    sh_request.status = Status.FAILED.value
                    sh_request.save()
                    err_msg = f"Failed to create SatData object from Sentinel Hub request."
                    logger.error(f"{err_msg} user='{request.user}', bbox='{bbox}', timestamp='{datetime.now()}'")
                    context["error"] = err_msg
                    return render(request, "sat_data_create_view.html", context)
                else:
                    sat_data.sh_request = sh_request
                    sat_data.save()
                    logger.debug(f"Added SHRequest object to SatData object. sat_data.id='{sat_data.id}'")

                    sh_request.status = Status.DONE.value
                    sh_request.save()
                    logger.debug(f"Set SHRequest status to 'DONE'. sh_request.id='{sh_request.id}'")

            except Exception as e:
                # Error: Excpetion raised
                sh_request.status = Status.FAILED.value
                sh_request.save()
                err_msg = f"Failed to request Sentinel Hub data."
                logger.debug(f"{err_msg} error='{e}', user='{request.user}', bbox='{bbox}', timestamp='{datetime.now()}'")
                context["error"] = err_msg
                return render(request, "sat_data_create_view.html", context)

            # Success
            success_msg = f"Sentinel Hub task scheduled. user='{request.user}', dir_name='{dir_name}', bbox='{bbox}', timestamp='{datetime.now()}'"
            logger.debug(success_msg)
            success_msg = f"Creation done! Calculations in progress..."
            context["success"] = success_msg
            context["sat_data_id"] = sat_data.id
        else:
            # Error: No bounding box coordinates
            # No SHRequest object created, so no status change needed
            err_msg = f"No bounding box data received."
            context["error"] = err_msg
            logger.error(f"{err_msg} user='{request.user}', timestamp='{datetime.now()}'")

    return render(request, "sat_data_create_view.html", context)


def wkt_to_coordinates_str(wkt) -> str:
    # Convert WKT to a GEOSGeometry object (if it's not one already)
    geom = GEOSGeometry(wkt)
    min_lon, min_lat, max_lon, max_lat = geom.extent

    return f"{min_lon},{min_lat},{max_lon},{max_lat}"

