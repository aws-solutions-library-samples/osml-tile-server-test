#  Copyright 2024 Amazon.com, Inc. or its affiliates.

from typing import Any, Dict

from requests import Session


def update_viewpoint(session: Session, url: str, viewpoint_id: str, test_body_data: Dict[str, Any]) -> None:
    """
    Test Case: Successfully update the viewpoint

    :param session: Requests session to use to send the request.
    :param url: URL to send the request to.
    :param viewpoint_id: Unique viewpoint id to get from the table.
    :param test_body_data: Test body data to pass through POST http method

    return: None
    """
    update_viewpoint_id = test_body_data
    update_viewpoint_id["viewpoint_id"] = viewpoint_id

    res = session.put(f"{url}", json=test_body_data)
    res.raise_for_status()

    response_data = res.json()

    assert res.status_code == 201
    assert response_data["viewpoint_name"] == test_body_data["viewpoint_name"]


def update_viewpoint_invalid_deleted(session: Session, url: str, viewpoint_id: str, test_body_data: Dict[str, Any]) -> None:
    """
    Test Case: Failed to update the viewpoint

    :param session: Requests session to use to send the request.
    :param url: URL to send the request to.
    :param viewpoint_id: Unique viewpoint id to get from the table.
    :param test_body_data: Test body data to pass through POST http method

    return: None
    """
    update_viewpoint_id = test_body_data
    update_viewpoint_id["viewpoint_id"] = viewpoint_id

    res = session.put(f"{url}", json=test_body_data)

    response_data = res.json()

    assert res.status_code == 404
    assert (
        "Cannot view ViewpointApiNames.UPDATE for this image since this has already been deleted." in response_data["detail"]
    )


def update_viewpoint_invalid_missing_field(
    session: Session, url: str, viewpoint_id: str, test_body_data: Dict[str, Any]
) -> None:
    """
    Test Case: Failed to update the viewpoint

    :param session: Requests session to use to send the request.
    :param url: URL to send the request to.
    :param viewpoint_id: Unique viewpoint id to get from the table.
    :param test_body_data: Test body data to pass through POST http method

    return: None
    """
    update_viewpoint_id = test_body_data
    update_viewpoint_id["viewpoint_id"] = viewpoint_id

    res = session.put(f"{url}", json=test_body_data)

    response_data = res.json()

    assert res.status_code == 422
    assert response_data["detail"][0]["msg"] == "Field required"
