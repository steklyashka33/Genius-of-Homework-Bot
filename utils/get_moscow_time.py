from datetime import datetime, timedelta, timezone

def get_moscow_time_from_dt(utc_dt: datetime) -> datetime:
    delta = timedelta(hours=3, minutes=0)
    return utc_dt + delta

def get_moscow_time_now() -> datetime:
    return get_moscow_time_from_dt(datetime.now(timezone.utc))


if __name__ == "__main__":
    print("Текущее московское время:", a:= get_moscow_time_now())