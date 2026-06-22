from collections import Counter


def analyze_log(uploaded_file):
    """
    Reads an uploaded infrastructure log and returns
    a structured summary for the AI agents.
    """

    text = uploaded_file.read().decode("utf-8")

    lines = text.splitlines()

    counts = Counter()

    max_temperature = 0

    for line in lines:

        upper = line.upper()

        if "WARNING" in upper:
            counts["warnings"] += 1

        if "ERROR" in upper:
            counts["errors"] += 1

        if "CRC" in upper:
            counts["crc_errors"] += 1

        if "RESET" in upper:
            counts["interface_resets"] += 1

        if "TEMPERATURE" in upper:

            for word in line.replace("(", " ").replace(")", " ").split():

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
    }