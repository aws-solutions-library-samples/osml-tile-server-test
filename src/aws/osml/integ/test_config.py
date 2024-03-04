#  Copyright 2024 Amazon.com, Inc. or its affiliates.

from typing import Any, Dict


class TileServerIntegTestConfig:
    def __init__(self, endpoint: str, s3_bucket: str, s3_key: str):
        # Tile Server
        self.endpoint = endpoint

        # S3
        self.test_bucket = s3_bucket
        self.test_object_key = s3_key

        # Viewpoint name
        self.test_viewpoint_name: str = "integ-test-viewpoint"

        # Test Data
        self.test_invalid_viewpoint_id: str = "invalid-viewpoint-id"

        self.test_viewpoint: Dict[str, Any] = {
            "bucket_name": self.test_bucket,
            "object_key": self.test_object_key,
            "viewpoint_name": self.test_viewpoint_name,
            "tile_size": 512,
            "range_adjustment": "NONE",
        }

        self.invalid_viewpoint: Dict[str, Any] = {
            "bucket_name": None,
            "object_key": self.test_object_key,
            "viewpoint_name": self.test_viewpoint_name,
            "tile_size": 512,
            "range_adjustment": "NONE",
        }

        self.valid_update_test_body: Dict[str, Any] = {
            "viewpoint_id": "",
            "viewpoint_name": "new-integ-test-viewpoint-name",
            "tile_size": 512,
            "range_adjustment": "NONE",
        }

        self.invalid_update_test_body: Dict[str, Any] = {
            "tile_size": 512,
            "range_adjustment": "NONE",
        }
