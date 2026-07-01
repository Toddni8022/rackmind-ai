from collections import Counter

from services.log_parser import line_severity


def analyze_log(uploaded_file):

    text = uploaded_file.read().decode("utf-8")

    lines = text.splitlines()

    counts = Counter()

    max_temperature = 0

    timeline = []

    for line in lines:

        # Severity comes from the log's level token, so message
        # text like "CRC error detected" is not counted as an error.
        severity = line_severity(line)

        if severity == "warning":
            counts["warnings"] += 1
        elif severity == "error":
            counts["errors"] += 1

        upper = line.upper()

        if "CRC ERROR" in upper:
            counts["crc_errors"] += 1

        if "RESET INITIATED" in upper:
            counts["interface_resets"] += 1

        if (
            "CRC ERROR" in upper
            or "TEMPERATURE THRESHOLD" in upper
            or "CRITICAL TEMPERATURE" in upper
            or "RESET INITIATED" in upper
        ):
            timeline.append(line)

        if "TEMPERATURE" in upper:

            for word in (
                line.replace("(", " ")
                .replace(")", " ")
                .split()
            ):

                if word.endswith("F"):

                    try:

                        value = int(word.replace("F", ""))

                        if value > max_temperature:
                            max_temperature = value

                    except ValueError:
                        pass

    return {
        "total_events": len(lines),
        "warnings": counts["warnings"],
        "errors": counts["errors"],
        "crc_errors": counts["crc_errors"],
        "interface_resets": counts["interface_resets"],
        "max_temperature": max_temperature,
        "timeline": timeline,
    }
