
import logging
import os
from threading import Thread
import uuid

from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import redirect, render, get_object_or_404

from sat_data.enums.sat_mission import SatMission
from sat_data.services.utils.file_utils import FileUtils
from sat_data.models import SatData, remove_media_root
from sat_data.forms import SatDataForm
from sat_data.services.attr_adder import AttrAdder
from dews.settings import VERSION, ARCHIVE_FILES_PATH

logger = logging.getLogger("django")


def details_view(request, sat_data_id):
    if not request.user.is_authenticated:
        logger.debug(
            f"User '{request.user}' is not authenticated to see details page of '{sat_data_id}'.")
        return redirect("login_view")

    # Get sat data obj
    sat_data: SatData = get_object_or_404(SatData, id=sat_data_id)

    context = {
        "version": VERSION,
        "sat_data": sat_data,
    }
    return render(request, "details_view.html", context)


def overview_view(request):
    if not request.user.is_authenticated:
        logger.debug(
            f"User '{request.user}' is not authenticated to see overview.")
        return redirect("login_view")

    context = {
        "version": VERSION,
        "sat_data_entries": SatData.objects.all(),
    }
    return render(request, "overview_view.html", context)


# def upload_view(request, error=None):
#     if not request.user.is_authenticated:
#         return redirect("login_view")


#     form = SatDataForm(request.POST or None, request.FILES or None)
#     logger.debug(f"Uploaded files: {request.FILES}")

#     context = {
#         "version": VERSION,
#         "error": error,
#         "form": form
#     }
#     return render(request, "upload_view.html", context)


def upload_view(request):
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
        name = request.POST.get("name", "")
        archive = request.FILES.get("archive")

        # Check user input
        if not name and not archive:
            return HttpResponseBadRequest("Name and archive file are required.")
        elif not name:
            return HttpResponseBadRequest("Name is required.")
        elif not archive:
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
                    f"Failed to write archive to file system. name='{name}', archive_path='{archive_path}', error='{e}'")
        else:
            # Archive already exists
            logger.info(f"Archive already exists. archive_path='{archive_path}'")

        # Extract and create SatData obj in background
        logger.debug(f"Create background task.")
        logger.info(
            f"Extract and create SatData obj. name='{name}', archive.name='{archive.name}', username='{request.user.username}', archive_path='{archive_path}'")
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
                f"Failed 'extract_and_create' background task. username='{request.user.username}', error='{e}'")
            err_msg = "Failed to extract and create archive. However, an entry was still created."
            context["error"] = err_msg
            logger.debug(
                f"Render 'upload_view.html' with error message: '{err_msg}'.")
            return render(request, "upload_view.html", context)

        # Upload done
        success_msg = "Upload done! Work in progress..."
        context["success"] = success_msg
        logger.debug(
            f"Render 'upload_view.html' with success message: '{success_msg}'.")
        return render(request, "upload_view.html", context)

    # GET request -> view and form
    logger.debug("Render 'upload_view.html'.")
    return render(request, "upload_view.html", context)


def __extract_and_create(request, archive_path: str, logger: logging.Logger = None):
    # Extract archive
    logger.info(f"Extracting archive. archive_path='{archive_path}'")
    mission = SatMission.get_mission_by_filename(archive_path)
    # Check if extracted directory exists
    extracted_path = FileUtils.extract_archive(archive_path, mission)
    logger.debug(f"Extracted path='{extracted_path}'")
    if extracted_path is None:
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
            # Add attributes (like mission, product type, band img paths, ...)
            logger.debug(f"Call AttrAdder. sat_data.id={sat_data.id}")
            attr_adder = AttrAdder(sat_data, extracted_path, mission)
            attr_adder.start()
            # Add paths
            logger.debug("YES")
            sat_data.extracted_path = remove_media_root(extracted_path)
            logger.debug("YESS")
            sat_data.archive = remove_media_root(archive_path)
            logger.debug("YESSS")
            sat_data.save()
            logger.debug("YESSSS")
            # Save successfull
            logger.info(
                f"Saved SatData. id='{sat_data.id}', extracted_path='{extracted_path}'")
            return
        except Exception as e:
            # Save failed
            logging.error(
                f"Failed to save SatData object. username='{request.user.username}', extracted_path='{extracted_path}', error='{e}'")
            return

        
