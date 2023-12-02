import shutil
import click
import zipfile
from backend.models.satellite_data.satellite_data import SatelliteData

from config import *
from backend.models.satellite_data.satellite_mission import SatelliteMission


@click.group()
def cli():
    pass


@cli.command("import")
@click.argument("filename", type=click.STRING)
@click.option("-m", "--mission", type=click.STRING, help="Satellite mission (e.g. 'sentinel-1a', 'sentinel-2b', etc.)")
def import_zip(filename, mission):
    # Check input
    if not filename:
        click.echo(
            "[ERROR] Please pass a valid file name of an archive that already exists on the system's filesystem ('dews_cli.py import <filename>').")
        return
    elif not mission:
        click.echo(
            "[ERROR] Please pass a mission using the '-m/--mission' flag (e.g. '-m sentinel-1a').")
        return
    else:
        filename = os.path.basename(filename)
        mission = mission.lower()  # needed in lowercase

    # Copy file to system's filesystem
    source_path = os.path.join(ZIP_FILES_PATH, filename)

    # Check if an extracted archive exist
    if os.path.exists(source_path):
        click.confirm(
            f"[PROMPT] This will overwrite previously imported data at destination '{source_path}'. Continue?", abort=True)

    # Extract zip archive
    extracted_path = extract_archive(source_path, mission)
    if extracted_path is None:
        click.echo(
            f"[ERROR] Could not extract archive. source_path='{source_path}', mission='{mission}'")
        return

    # Create SatelliteData object
    # Check if mission is valid
    if not create_sd_obj(source_path, mission, extracted_path):
        click.echo(
            f"[ERROR] Could not create a SatelliteData object. source_path='{source_path}', mission='{mission}'")
        return


def extract_archive(source_path: str, mission: str):
    if not os.path.exists(source_path):
        click.echo(
            f"[ERROR] Cannot extract archive because archive does not exist. source_path='{source_path}', mission='{mission}'")
        return None

    try:
        with zipfile.ZipFile(source_path, 'r') as zip_ref:
            folder_name, _ = os.path.splitext(os.path.basename(source_path))
            destination_path = os.path.join(EXTRACTED_FILES_PATH, mission)
            zip_ref.extractall(destination_path)
            extracted_path = os.path.join(destination_path, folder_name)
    except Exception as e:
        click.echo(
            f"[ERROR] Failed to extract all files from archive. source_path='{source_path}', extracted_path='{extracted_path}', mission='{mission}', error='{e}'")
        return None

    if os.path.exists(extracted_path):
        click.echo(
            f"[INFO] Extracted archive from '{source_path}' to '{extracted_path}'.")
        return extracted_path
    else:
        click.echo(f"[ERROR] Directory at '{extracted_path}' does not exist.")
        return None


def create_sd_obj(source_path: str, mission: str, extracted_path: str):
    if not mission.lower() in [satellite_mission.value.lower() for satellite_mission in SatelliteMission]:
        click.echo(
            f"[ERROR] Mission '{mission}' is not a valid satellite mission! Please use e.g. 'sentinel-1a' or 'sentinel-2b'.")
        return False
    try:
        # Create SatelliteData object
        SatelliteData.create(
            directory_path=extracted_path,
            user_id=DB_USER,
            mission=mission
        )
        click.echo(
            f"[INFO] Created a SatelliteData object. directory_path='{extracted_path}', user_id='{DB_USER}', mission='{mission}'")
        return True
    except Exception as e:
        click.echo(
            f"[ERROR] Failed to create SatelliteData object. error='{e}', source_path='{source_path}', mission='{mission}'")
        return False


@cli.command("export")
@click.argument("id")
@click.option("-d", "--destination", type=click.Path(), help="Export path")
def export_zip(id, destination):
    # Check input
    if not id or not destination:
        click.echo(
            "[ERROR] Please pass a satellite data id and the destination export path!")
        return

    # TODO: search for id's source path in database
    source = ""
    try:
        shutil.copy(source, destination)
    except FileNotFoundError:
        click.echo(f"[ERROR] File not found at source '{source}'.")
    except PermissionError:
        click.echo(
            f"[ERROR] Permission denied to copy file from source '{source}' to destination '{destination}'.")
    except Exception as e:
        click.echo(f"[ERROR] {e}")
    pass


@cli.command("index")
@click.option("-i", "--id", help="Satellite data id")
@click.option("-n", "--name", help="Name of index (e.g. 'ndvi', 'evi', 'moisture', ...)")
@click.option("-p", "--picture", type=click.BOOL, help="Set to 'True' if you want to download the index image.")
@click.option("-v", "--value", type=click.BOOL, help="Set to 'True' if you want to display the index value.")
def index(id, name, picture, value):
    if picture and value:
        click.echo(
            "[ERROR] You can either export an index image ('-p') or get the index value ('-v'). Not both!")
    pass

if __name__ == '__main__':
    cli()
