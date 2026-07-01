"""
RackMind AI

Simulator Connector

Generates realistic rack telemetry without any external
infrastructure so demos, development, and the trend dashboard
work out of the box.
"""

import math
import random
from datetime import datetime, timedelta

from connectors.base import TelemetryConnector


class SimulatorConnector(TelemetryConnector):

    name = "simulator"
    description = "Built-in demo telemetry generator"

    def __init__(
        self,
        racks: list[str] = None,
        samples: int = 12,
        interval_minutes: int = 5,
        seed: int = None,
        failing_rack: str = None,
    ):
        self.racks = racks or ["Rack-22", "Rack-07", "Rack-14"]
        self.samples = samples
        self.interval_minutes = interval_minutes
        self.random = random.Random(seed)
        # One rack trends toward critical so predictions have
        # something interesting to flag.
        self.failing_rack = failing_rack or self.racks[0]

    def fetch(self) -> list[dict]:
        readings = []

        start = datetime.now() - timedelta(
            minutes=self.interval_minutes * (self.samples - 1)
        )

        for rack in self.racks:
            failing = rack == self.failing_rack

            base_temp = 84.0 if failing else self.random.uniform(66, 74)
            base_power = 4.2 if failing else self.random.uniform(2.8, 3.6)

            crc_total = 0
            reset_total = 0

            for index in range(self.samples):
                progress = index / max(1, self.samples - 1)

                wobble = math.sin(index / 2) * 1.5

                if failing:
                    temperature = base_temp + (progress * 10) + wobble
                    power = base_power + (progress * 0.8)
                    crc_total += self.random.randint(0, 3)

                    if temperature > 90:
                        reset_total += self.random.randint(0, 1)
                else:
                    temperature = base_temp + wobble
                    power = base_power + self.random.uniform(-0.1, 0.1)

                timestamp = start + timedelta(
                    minutes=self.interval_minutes * index
                )

                readings.append(
                    self.normalize(
                        rack,
                        timestamp=timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                        temperature=round(temperature, 1),
                        humidity=round(self.random.uniform(40, 52), 1),
                        power_kw=round(power, 2),
                        crc_errors=crc_total,
                        resets=reset_total,
                    )
                )

        return readings
