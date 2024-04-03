
from concurrent.futures import ThreadPoolExecutor
import logging
import os
from threading import Thread
import uuid
from requests import HTTPError
from sentinelhub import MimeType, DataCollection
from datetime import datetime
import json

from django.contrib.gis.geos import Polygon
from django.core.serializers import serialize
from django.http import HttpResponseBadRequest, JsonResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.views.decorators.http import require_POST

from sat_data.enums.sat_mission import SatMission
from sat_data.services.utils.file_utils import FileUtils
from sat_data.models import SatData, TimeTravel, remove_media_root
from sat_data.forms import SatDataForm
from sat_data.services.attr_adder import AttrAdder
from sat_data.services.metrics_calc import MetricsCalculator
from sat_data.services.sentinel_hub import request_sat_data
from dews.settings import MEDIA_ROOT, VERSION, ARCHIVE_FILES_PATH
from sentinelhub import SentinelHubRequest
from django.db import connection

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


def sat_data_upload_view(request):
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

    # Context
    context = {
        "version": VERSION,
        "error": None,  # will be overwritten, if needed
        "success": None,  # will be overwritten, if needed
        "form": SatDataForm(request.POST or None, request.FILES or None)
    }

    # POST request -> create SatData obj
    if request.method == "POST":
        archive = request.FILES.get("archive")

        # Check user input
        if not archive:
            return HttpResponseBadRequest("Archive file is required.")

        # Write archive to file system
        archive_path = ARCHIVE_FILES_PATH / archive.name
        if not os.path.exists(archive_path):
            # Archive does not exist
            logger.info(
                f"Archive does not exist. Will write archive to file system. archive_path='{archive_path}'")
            try:
                with open(archive_path, "wb+") as file_ref:
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

        # Extract and create SatData obj in background
        try:
            ok = create_sat_data(request, archive_path)
            if ok:
                pass
            else:
                raise Exception(f"Failed to create SatData object. ok='{ok}'")
        except Exception as e:
            # Background task failed
            logger.error(
                f"Failed 'extract_and_create' background task. username='{request.user.username}', error='{e}'")
            err_msg = "Failed to extract and create archive. However, an entry was still created."
            context["error"] = err_msg
            logger.debug(
                f"Render 'sat_data_upload_view.html' with error message: '{err_msg}'.")
            return render(request, "sat_data_upload_view.html", context)

        # Upload done
        success_msg = f"Upload done! Work in progress... archive='{archive.name}'"
        context["success"] = success_msg
        logger.debug(
            f"Render 'sat_data_upload_view.html' with success message: '{success_msg}'.")
        return render(request, "sat_data_upload_view.html", context)

    # GET request -> view and form
    logger.debug("Render 'sat_data_upload_view.html'.")
    return render(request, "sat_data_upload_view.html", context)


def create_sat_data(request, archive_path) -> bool:
    logger.debug(f"Create background task.")
    logger.info(
        f"Extract and create SatData obj. username='{request.user.username}', archive_path='{archive_path}'")
    # Start background task
    thread = Thread(target=__extract_and_create,
                    args=(request, str(archive_path), logger))
    thread.start()
    logger.debug(
        f"Started 'extract_and_create' background task. username='{request.user.username}', archive_path='{archive_path}'")
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

            # Calculate metrics
            logger.debug(f"Calling MetricsCalculator. sat_data.id='{sat_data.id}', extracted_path='{extracted_path}', mission='{mission}', product_type='{sat_data.product_type}'")
            metrics_to_calc = ["ndvi", "rgb"]
            mc = MetricsCalculator(
                sat_data=sat_data,
                metrics_to_calc=metrics_to_calc)
            mc.start()
            logger.info(f"Metrics calculation done. metrics_to_calc='{metrics_to_calc}', sat_data.id='{sat_data.id}'")

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


def create_sh_sat_data(request, data_folder, dir_name, bbox, bands) -> bool:
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
        )
        attr_adder.start()
        logger.info(
            f"Created SatData with several attributes. id='{sat_data.id}', extracted_path='{extracted_path}'")

        # Calculate metrics
        logger.debug(f"Calling MetricsCalculator. sat_data.id='{sat_data.id}', extracted_path='{extracted_path}', sat_data.mission='{sat_data.mission}', sat_data.product_type='{sat_data.product_type}'")
        metrics_to_calc = ["ndvi", "rgb"]
        mc = MetricsCalculator(
            sat_data=sat_data,
            metrics_to_calc=metrics_to_calc)
        mc.start()
        logger.info(f"Metrics calculation done. metrics_to_calc='{metrics_to_calc}', sat_data.id='{sat_data.id}'")

        return True
    except Exception as e:
        logger.error(
            f"Failed to create SatData object from Sentinel Hub request. user='{request.user}', error='{e}'")
        return False


@require_POST
def sentinel_hub_request_view(request):
    # Extract bounds data from POST request
    logger.debug("Sentinel Hub Request request: ", request)
    try:
        data = json.loads(request.body)
        logger.debug("Sentinel Hub Request JSON: ", data)
    except json.JSONDecodeError as e:
        return JsonResponse(
            {
                "status": "error",
                "message": f"Invalid JSON data. error='{e}'",
            }, status=400)

    if not all(k in data for k in ('bounds', 'mission', 'bands', 'startDate', 'endDate', 'resolution')):
        return JsonResponse(
            {
                "status": "error",
                "message": "Missing required fields",
            }, status=400)

    bounds = data.get('bounds')
    mission = data.get('mission')
    bands = data.get('bands')
    start_date = data.get('startDate')
    end_date = data.get('endDate')
    resolution = data.get('resolution')
    data_folder = f"{MEDIA_ROOT}/sentinel_hub"

    if bounds:
        # Create tuple
        bbox = tuple(float(bound) for bound in bounds.split(','))
        if mission == "SENTINEL2_L1C":
            data_collection = DataCollection.SENTINEL2_L1C
        else:
            data_collection = DataCollection.SENTINEL2_L2A
        mission = SatMission.SENTINEL_2B

        # Prepare your task parameters
        try:
            response = request_sat_data(
                bbox=bbox,
                resolution=int(resolution),
                data_folder=data_folder,
                data_collection=data_collection,
                mimetypes=[MimeType.TIFF, MimeType.PNG],
                bands=bands,
                start_date=datetime.strptime(start_date, '%Y-%m-%d'),
                end_date=datetime.strptime(end_date, '%Y-%m-%d'),
            )
            logger.debug(f"Requesting Sentinel Hub data done. bbox='{bbox}', resolution='{resolution}', data_folder='{data_folder}', data_collection='{data_collection}', bands='{bands}', start_date='{start_date}', end_date='{end_date}'")

            dir_name = response.get_filename_list()[0].split('/')[0]
            logger.debug(f"Create SatData object from Sentinel Hub request. user='{request.user}', dir_name='{dir_name}', bbox='{bbox}', timestamp='{datetime.now()}'")
            ok = create_sh_sat_data(
                request, data_folder, dir_name, bbox, bands)
            if not ok:
                logger.debug(f"Failed to create SatData object from Sentinel Hub request. user='{request.user}', bbox='{bbox}', timestamp='{datetime.now()}'")
                return JsonResponse(
                    {
                        "status": "error",
                        "message": f"Could not create SatData object from Sentinel Hub request. user='{request.user}', bbox='{bbox}', timestamp='{datetime.now()}'",
                    }, status=400)
        except Exception as e:
            # Error
            logger.debug(f"Failed to request Sentinel Hub data. error='{e}', user='{request.user}', bbox='{bbox}', timestamp='{datetime.now()}'")
            return JsonResponse(
                {
                    "status": "error",
                    "message": str(e),
                }, status=400)

        # Success
        msg = f"Sentinel Hub task scheduled. user='{request.user}', dir_name='{dir_name}', bbox='{bbox}', timestamp='{datetime.now()}'"
        logger.debug(msg)

        return JsonResponse(
            {
                "status": "success",
                "message": msg,
            }, status=200)
    else:
        # Error
        msg = f"No bounding box data received. user='{request.user}', timestamp='{datetime.now()}"
        logger.error(msg)

        return JsonResponse(
            {
                "status": "error",
                "message": msg,
            }, status=400)
