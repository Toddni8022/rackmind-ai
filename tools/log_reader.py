from services.log_parser import build_log_timeline, parse_log


def analyze_log(uploaded_file):

    text = uploaded_file.read().decode("utf-8")

    summary = parse_log(text)

    return {
        "total_events": summary["events"],
        "warnings": summary["warnings"],
        "errors": summary["errors"],
        "crc_errors": summary["crc_errors"],
        "interface_resets": summary["resets"],
        "max_temperature": summary["max_temp"],
        "timeline": build_log_timeline(text),
    }
