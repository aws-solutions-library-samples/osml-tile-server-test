#  Copyright 2024 Amazon.com, Inc. or its affiliates.

from requests import Session


def describe_viewpoint(session: Session, url: str, viewpoint_id: str) -> None:
    """
    Test Case: Successfully describe a viewpoint

    :param session: Requests session to use to send the request.
    :param url: URL to send the request to.
    :param viewpoint_id: Unique viewpoint id to get from the table.

    return: None
    """
    res = session.get(f"{url}/{viewpoint_id}")
    res.raise_for_status()

    response_data = res.json()

    assert res.status_code == 200
    assert response_data["viewpoint_id"] == viewpoint_id
    assert response_data["viewpoint_status"] != "DELETED"


def describe_viewpoint_invalid(session: Session, url: str, viewpoint_id: str) -> None:
    """
    Test Case: Failed to describe a viewpoint

    :param session: Requests session to use to send the request.
    :param url: URL to send the request to.
    :param viewpoint_id: Unique viewpoint id to get from the table.

    return: None
    """
    res = session.get(f"{url}/{viewpoint_id}")

    response_data = res.json()

    assert res.status_code == 500
    assert "Invalid Key, it does not exist in ViewpointStatusTable" in response_data["detail"]
