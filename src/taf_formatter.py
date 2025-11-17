
def generate_taf(data):
    icao = data.get("icao", "")
    issue_time = data.get("issue_time", "")
    time_from = data.get("time_from", "")
    time_to = data.get("time_to", "")
    wind_dir = int(data.get("wind_dir") or 0)
    wind_speed = int(data.get("wind_speed") or 0)
    visibility = int(data.get("visibility") or 0)
    clouds = data.get("clouds", "")
    weather_events = data.get("weather_events") or []

    weather_str = " ".join(weather_events) if weather_events else "NSW"

    if not data.get("group_type"):  # MAIN
        taf = (
            f"TAF {icao} {issue_time}Z "
            f"{time_from}/{time_to} "
            f"{wind_dir:03d}{wind_speed:02d}MPS "
            f"{visibility} {weather_str} {clouds}"
        )
    else:  # группа
        taf = (
            f"{data.get('group_type')} {time_from}/{time_to} "
            f"{wind_dir:03d}{wind_speed:02d}MPS "
            f"{visibility} {weather_str} {clouds}"
        )

    return taf