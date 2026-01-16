import json

import pytest
from pydantic import ValidationError
from typer.testing import CliRunner

from immich import AsyncClient
from immich.cli.app import app as cli_app
from immich.client import AlbumResponseDto
from immich.client.models.activity_response_dto import ActivityResponseDto
from immich.client.models.license_response_dto import LicenseResponseDto
from immich.client.models.reaction_type import ReactionType

########################################################
# Constants for CLI testing
########################################################
ACTIVATION_KEY = "4kJUNUWMq13J14zqPFm1NodRcI6MV6DeOGvQNIgrM8Sc9nv669wyEVvFw1Nz4Kb1W7zLWblOtXEQzpRRqC4r4fKjewJxfbpeo9sEsqAVIfl4Ero-Vp1Dg21-sVdDGZEAy2oeTCXAyCT5d1JqrqR6N1qTAm4xOx9ujXQRFYhjRG8uwudw7_Q49pF18Tj5OEv9qCqElxztoNck4i6O_azsmsoOQrLIENIWPh3EynBN3ESpYERdCgXO8MlWeuG14_V1HbNjnJPZDuvYg__YfMzoOEtfm1sCqEaJ2Ww-BaX7yGfuCL4XsuZlCQQNHjfscy_WywVfIZPKCiW8QR74i0cSzQ"
LICENSE_KEY = "IMSV-6ECZ-91TE-WZRM-Q7AQ-MBN4-UW48-2CPT-71X9"


@pytest.fixture
def runner(client_with_api_key: AsyncClient) -> CliRunner:
    """Typer CliRunner fixture for CLI testing."""
    return CliRunner(
        env={
            "IMMICH_API_URL": client_with_api_key.base_client.configuration.host,
            "IMMICH_API_KEY": client_with_api_key.base_client.configuration.api_key[
                "api_key"
            ],
        }
    )


########################################################
# Fixtures for CLI commands depending on other commands
########################################################
@pytest.fixture
def album(runner: CliRunner) -> AlbumResponseDto:
    """Fixture to set up album for testing.

    Creates an album, returns parsed album object.
    Skips dependent tests if album creation fails.
    """
    # Set up: Create album
    album_result = runner.invoke(
        cli_app,
        [
            "--format",
            "json",
            "albums",
            "create-album",
            "--albumName",
            "Test Album for Activities",
        ],
    )

    if album_result.exit_code != 0:
        pytest.skip(
            f"Album creation failed:\n{album_result.stdout}{album_result.stderr}"
        )

    try:
        album = AlbumResponseDto.model_validate(json.loads(album_result.output))
    except (ValidationError, json.JSONDecodeError) as e:
        pytest.skip(
            f"Album creation returned invalid JSON:\n{e}\n{album_result.output}"
        )

    yield album

    # Cleanup: Delete album (only runs if we got here, i.e., album parsed successfully)
    if album.id:
        runner.invoke(
            cli_app,
            ["--format", "json", "albums", "delete-album", str(album.id)],
        )


@pytest.fixture
def activity(
    runner: CliRunner, album: AlbumResponseDto, activity_type: ReactionType
) -> ActivityResponseDto:
    """Fixture to set up activity for testing.

    Creates an activity with the specified type, returns parsed activity object.
    Skips dependent tests if activity creation fails.
    """
    # Set up: Create activity
    activity_args = [
        "--format",
        "json",
        "activities",
        "create-activity",
        "--albumId",
        str(album.id),
        "--type",
        activity_type.value,
    ]
    if activity_type == ReactionType.COMMENT:
        activity_args.extend(["--comment", "Test comment"])

    activity_result = runner.invoke(cli_app, activity_args)

    if activity_result.exit_code != 0:
        pytest.skip(
            f"Activity creation failed ({activity_type.value}):\n{activity_result.stdout}{activity_result.stderr}"
        )

    try:
        activity = ActivityResponseDto.model_validate(
            json.loads(activity_result.output)
        )
    except (ValidationError, json.JSONDecodeError) as e:
        pytest.skip(
            f"Activity creation returned invalid JSON:\n{e}\n{activity_result.output}"
        )

    yield activity

    # Cleanup: Delete activity (only runs if we got here, i.e., activity parsed successfully)
    if activity.id:
        runner.invoke(
            cli_app,
            ["--format", "json", "activities", "delete-activity", str(activity.id)],
        )


@pytest.fixture
def license(runner: CliRunner) -> LicenseResponseDto:
    """Fixture to set up license for testing.

    Sets a license, returns parsed license object.
    Skips dependent tests if license setup fails.
    Note: This requires valid license keys. Tests may skip if license keys are not available.
    """
    # Set up: Create license
    result = runner.invoke(
        cli_app,
        [
            "--format",
            "json",
            "server",
            "set-server-license",
            "--licenseKey",
            LICENSE_KEY,
            "--activationKey",
            ACTIVATION_KEY,
        ],
    )

    if result.exit_code != 0:
        pytest.skip(f"License setup failed:\n{result.stdout}{result.stderr}")

    try:
        license_obj = LicenseResponseDto.model_validate(json.loads(result.output))
    except (ValidationError, json.JSONDecodeError) as e:
        pytest.skip(f"License setup returned invalid JSON:\n{e}\n{result.output}")

    yield license_obj

    # Cleanup: Delete license (only runs if we got here, i.e., license parsed successfully)
    runner.invoke(
        cli_app,
        ["--format", "json", "server", "delete-server-license"],
    )
