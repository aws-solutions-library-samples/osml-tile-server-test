#  Copyright 2024 Amazon.com, Inc. or its affiliates.

from requests import Session


def get_info(session: Session, url: str, viewpoint_id: str) -> None:
    """
    Test Case: Successfully get the info of the viewpoint

    :param session: Requests session to use to send the request.
    :param url: URL to send the request to.
    :param viewpoint_id: Unique viewpoint id to get from the table.

    return: None
    """
    res = session.get(f"{url}/{viewpoint_id}/info")
    res.raise_for_status()

    assert res.status_code == 200


def get_info_invalid(session: Session, url: str, viewpoint_id: str) -> None:
    """
    Test Case: Failed to get the info of the viewpoint

    :param session: Requests session to use to send the request.
    :param url: URL to send the request to.
    :param viewpoint_id: Unique viewpoint id to get from the table.

    return : None
    """
    res = session.get(f"{url}/{viewpoint_id}/info")

    response_data = res.json()

    assert res.status_code == 404
    assert (
        "Cannot view ViewpointApiNames.INFO for this image since this has already been deleted." in response_data["detail"]
    )
