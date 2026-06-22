from collections import Counter


def analyze_log(uploaded_file):
    """
    Reads a log file and returns a structured summary.
    """

    text = uploaded_file.read().decode("utf-8")

    lines = text.splitlines()

    summary = Counter()

    max_temp = 0

    for line in lines:

        upper = line.upper()

        if "WARNING" in upper:
            summary["warnings"] += 1

        if "ERROR" in upper:
            summary["errors"] += 1

        if "CRC" in upper:
            summary["crc_errors"] += 1

        if "RESET" in upper:
            summary["interface_resets"] += 1

        if "TEMPERATURE" in upper:

            parts = line.replace("(", " ").replace(")", " ").split()

            for part in parts:

                if part.endswith("F"):

                    try:

                        value = int(part.replace("F", ""))

                        max_temp = max(max_temp, value)

                    except ValueError:

                        pass

    return {
        "total_events": len(lines),
        "warnings": summary["warnings"],
        "errors": summary["errors"],
        "crc_errors": summary["crc_errors"],
        "interface_resets": summary["interface_resets"],
        "max_temperature": max_temp,
    }