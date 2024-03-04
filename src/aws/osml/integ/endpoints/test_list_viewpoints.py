#  Copyright 2024 Amazon.com, Inc. or its affiliates.

from requests import Session


def list_viewpoints(session: Session, url: str) -> None:
    """
    Test Case: Successfully get the list of the viewpoints

    :param session: Requests session to use to send the request.
    :param url: URL to send the request to.

    return: None
    """
    res = session.get(url)
    res.raise_for_status()

    response_data = res.json()

    assert res.status_code == 200
    assert len(response_data["items"]) > 0
