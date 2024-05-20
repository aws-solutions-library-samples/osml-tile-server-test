#  Copyright 2024 Amazon.com, Inc. or its affiliates.

from requests import Session


def get_statistics(session: Session, url: str, viewpoint_id: str) -> None:
    """
    Test Case: Successfully get the statistics of the viewpoint

    :param session: Requests session to use to send the request.
    :param url: URL to send the request to.
    :param viewpoint_id: Unique viewpoint id to get from the table.

    return: None
    """
    res = session.get(f"{url}/{viewpoint_id}/image/statistics")
    res.raise_for_status()

    response_data = res.json()

    assert res.status_code == 200

    assert response_data["image_statistics"]["geoTransform"] is not None
    assert response_data["image_statistics"]["cornerCoordinates"] is not None
    assert response_data["image_statistics"]["bands"] is not None


def get_statistics_invalid(session: Session, url: str, viewpoint_id: str) -> None:
    """
    Test Case: Failed to get the statistics of the viewpoint

    :param session: Requests session to use to send the request.
    :param url: URL to send the request to.
    :param viewpoint_id: Unique viewpoint id to get from the table.

    return: None
    """
    res = session.get(f"{url}/{viewpoint_id}/image/statistics")

    response_data = res.json()

    assert res.status_code == 404
    assert (
        "Cannot view ViewpointApiNames.STATISTICS for this image since this has already been deleted."
        in response_data["detail"]
    )
