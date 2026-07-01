"""
RackMind AI

CloudWatch Connector

Pulls rack telemetry from AWS CloudWatch custom metrics (the
common pattern for sites shipping DC sensor data to the cloud).
Requires the optional boto3 package.
"""

from datetime import datetime, timedelta

from connectors.base import ConnectorError, TelemetryConnector

DEFAULT_METRIC_NAMES = {
    "temperature": "RackTemperature",
    "humidity": "RackHumidity",
    "power_kw": "RackPowerKW",
}


class CloudWatchConnector(TelemetryConnector):

    name = "cloudwatch"
    description = "AWS CloudWatch custom metrics"

    def __init__(
        self,
        namespace: str = "DataCenter",
        region: str = "us-east-1",
        rack_dimension: str = "Rack",
        racks: list[str] = None,
        metric_names: dict = None,
        lookback_minutes: int = 60,
    ):
        self.namespace = namespace
        self.region = region
        self.rack_dimension = rack_dimension
        self.racks = racks or []
        self.metric_names = metric_names or dict(DEFAULT_METRIC_NAMES)
        self.lookback_minutes = lookback_minutes

    def _client(self):
        try:
            import boto3
        except ImportError as ex:
            raise ConnectorError(
                "CloudWatch support requires the boto3 package. "
                "Install it with: pip install boto3"
            ) from ex

        try:
            return boto3.client("cloudwatch", region_name=self.region)
        except Exception as ex:
            raise ConnectorError(
                f"Unable to create a CloudWatch client: {ex}. "
                "Check AWS credentials and region."
            ) from ex

    def fetch(self) -> list[dict]:
        if not self.racks:
            raise ConnectorError(
                "At least one rack name is required for the "
                f"'{self.rack_dimension}' dimension."
            )

        client = self._client()

        end = datetime.utcnow()
        start = end - timedelta(minutes=self.lookback_minutes)

        readings = []

        for rack in self.racks:
            metrics = {}

            for metric, metric_name in self.metric_names.items():
                if not metric_name:
                    continue

                try:
                    response = client.get_metric_statistics(
                        Namespace=self.namespace,
                        MetricName=metric_name,
                        Dimensions=[
                            {
                                "Name": self.rack_dimension,
                                "Value": rack,
                            }
                        ],
                        StartTime=start,
                        EndTime=end,
                        Period=300,
                        Statistics=["Average"],
                    )
                except Exception as ex:
                    raise ConnectorError(
                        f"CloudWatch query for {metric_name} failed: {ex}"
                    ) from ex

                datapoints = sorted(
                    response.get("Datapoints", []),
                    key=lambda point: point["Timestamp"],
                )

                if datapoints:
                    metrics[metric] = datapoints[-1]["Average"]

            if metrics:
                readings.append(self.normalize(rack, **metrics))

        if not readings:
            raise ConnectorError(
                f"CloudWatch returned no datapoints in namespace "
                f"'{self.namespace}' for the configured racks."
            )

        return readings
