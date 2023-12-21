
import logging
import os
from threading import Thread
import uuid

from django.core.serializers import serialize
from django.http import HttpResponseBadRequest
from django.shortcuts import redirect, render, get_object_or_404

from sat_data.enums.sat_mission import SatMission
from sat_data.services.utils.file_utils import FileUtils
from sat_data.models import SatData, TimeTravel, remove_media_root
from sat_data.forms import SatDataForm
from sat_data.services.attr_adder import AttrAdder
from dews.settings import VERSION, ARCHIVE_FILES_PATH

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
        context["time_travel_geojson"] = serialize("geojson", [time_travel], geometry_field="leaflet_coordinates", fields=())
    else:
        context["time_travel_geojson"] = None

    return render(request, "time_travel_details_view.html", context)


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
    }

    # Create GeoJSON
    if sat_data.coordinates:
        context["sat_data_geojson"] = serialize('geojson', [sat_data], geometry_field='leaflet_coordinates', fields=())
    else:
        context["sat_data_geojson"] = None

    return render(request, "sat_data_details_view.html", context)


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
        sat_data_entries = sat_data_entries.filter(name__icontains=search_query)
        time_travel_entries = time_travel_entries.filter(name__icontains=search_query)

    # Filter by mission if it exists
    mission_query = request.GET.get('mission', '')
    if mission_query:
        sat_data_entries = sat_data_entries.filter(mission=mission_query)
        time_travel_entries = time_travel_entries.filter(mission=mission_query)

    # Filter by product type if it exists
    prod_type_query = request.GET.get('product_type', '')
    if prod_type_query:
        sat_data_entries = sat_data_entries.filter(product_type=prod_type_query)
        time_travel_entries = time_travel_entries.filter(product_type=prod_type_query)

    logger.debug(f"Search query: '{search_query}', Mission query: '{mission_query}', Product type query: '{prod_type_query}'")

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
            logger.info(f"Archive does not exist. Will write archive to file system. archive_path='{archive_path}'")
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
            logger.info(f"Archive already exists. archive_path='{archive_path}'")

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
        success_msg = "Upload done! Work in progress..."
        context["success"] = success_msg
        logger.debug(
            f"Render 'sat_data_upload_view.html' with success message: '{success_msg}'.")
        return render(request, "sat_data_upload_view.html", context)

    # GET request -> view and form
    logger.debug("Render 'sat_data_upload_view.html'.")
    return render(request, "sat_data_upload_view.html", context)


def create_sat_data(request, archive_path) -> bool:
    logger.debug(f"Create background task.")
    logger.info(f"Extract and create SatData obj. username='{request.user.username}', archive_path='{archive_path}'")
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
            logger.debug(f"Created form, added id and user. id='{sat_data.id}'")
            
            # Add paths
            sat_data.archive = remove_media_root(archive_path)
            logger.debug(f"Added archive file. sat_data.id='{sat_data.id}'")
            sat_data.extracted_path = remove_media_root(extracted_path)
            logger.debug(f"Added extracted path. sat_data.id='{sat_data.id}'")

            # Add attributes (like mission, product type, band img paths, ...)
            logger.debug(f"Calling AttrAdder. sat_data.id='{sat_data.id}'")
            attr_adder = AttrAdder(sat_data, extracted_path, mission)
            attr_adder.start()
            logger.debug(f"AttrAdder done. sat_data.id='{sat_data.id}'")

            # Final save
            logger.debug(f"Before final save. sat_data.id='{sat_data.id}'")
            sat_data.save()
            logger.debug(f"Final save. id='{sat_data.id}'")
            logger.info(
                f"Saved SatData with all added attributes. id='{sat_data.id}', extracted_path='{extracted_path}'")
            return
        except Exception as e:
            # Save failed
            logging.error(
                f"Failed to create, add attributes and save a SatData object. username='{request.user.username}', extracted_path='{extracted_path}', error='{e}'")
            return
    else:
        # Form is not valid
        logger.error(
            f"Form is not valid. username='{request.user.username}', extracted_path='{extracted_path}', form='{form}'")
        return

        
