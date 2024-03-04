#  Copyright 2024 Amazon.com, Inc. or its affiliates.

from typing import Any, Dict

from requests import Session


def create_viewpoint(session: Session, url: str, test_body_data: Dict[str, Any]) -> str:
    """
    Test Case: Successfully create a viewpoint

    :param session: Requests session to use to send the request.
    :param url: URL to send the request to.
    :param test_body_data: Test body data to pass through POST http method.

    return str: Viewpoint_id or the created viewpoint
    """
    res = session.post(url, json=test_body_data)
    res.raise_for_status()

    assert res.status_code == 201
    response_data = res.json()
    assert response_data.get("viewpoint_id") is not None
    assert response_data.get("viewpoint_status") == "REQUESTED"
    return response_data["viewpoint_id"]


def create_viewpoint_invalid(session: Session, url: str, test_body_data: Dict[str, Any]) -> None:
    """
    Test Case: Failed to create a viewpoint

    :param test_body_data: Test body data to pass through POST http method

    return: None
    """
    res = session.post(url, json=test_body_data)

    response_data = res.json()

    assert res.status_code == 422
    assert response_data["detail"][0]["msg"] == "Input should be a valid string"
