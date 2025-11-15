
def generate_taf(data):
    weather_str = " ".join(data["weather_events"]) if data["weather_events"] else "NSW"

    taf = (
        f"TAF {data['icao']} {data['issue_time']}Z "
        f"{data['time_from']}/{data['time_to']} "
        f"{data['wind_dir']:03d}{data['wind_speed']:02d}MPS "
        f"{data['visibility']} {weather_str} {data['clouds']}\n"
    )
    return taf