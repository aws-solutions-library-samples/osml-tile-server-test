#  Copyright 2024 Amazon.com, Inc. or its affiliates.

from requests import Session


def get_bounds(session: Session, url: str, viewpoint_id: str) -> None:
    """
    Test Case: Successfully get the bounds of the viewpoint

    :param session: Requests session to use to send the request.
    :param url: URL to send the request to.
    :param viewpoint_id: Unique viewpoint id to get from the table.

    return: None
    """
    res = session.get(f"{url}/{viewpoint_id}/bounds")
    res.raise_for_status()

    response_data = res.json()

    assert res.status_code == 200
    assert response_data["bounds"] is not None


def get_bounds_invalid(session: Session, url: str, viewpoint_id: str) -> None:
    """
    Test Case: Failed to get the bounds of the viewpoint

    :param session: Requests session to use to send the request.
    :param url: URL to send the request to.
    :param viewpoint_id: Unique viewpoint id to get from the table.

    return: None
    """
    res = session.get(f"{url}/{viewpoint_id}/bounds")

    response_data = res.json()

    assert res.status_code == 404
    assert (
        "Cannot view ViewpointApiNames.BOUNDS for this image since this has already been deleted." in response_data["detail"]
    )
