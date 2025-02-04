from datetime import date, datetime, timedelta


def get_seasonal_offset(now) -> int:
    """
    Based on :
    https://stackoverflow.com/questions/16139306/determine-season-given-timestamp-in-python-using-datetime
    """

    Y = 2000  # dummy leap year to allow input X-02-29 (leap day)
    seasons = [
        ("winter", (date(Y, 1, 1), date(Y, 3, 20))),
        ("spring", (date(Y, 3, 21), date(Y, 6, 20))),
        ("summer", (date(Y, 6, 21), date(Y, 9, 22))),
        ("autumn", (date(Y, 9, 23), date(Y, 12, 20))),
        ("winter", (date(Y, 12, 21), date(Y, 12, 31))),
    ]
    if isinstance(now, datetime):
        now = now.date()
    now = now.replace(year=Y)
    if next(season for season, (start, end) in seasons if start <= now <= end) in (
        "spring",
        "summer",
    ):
        return -2
    return -1


def parse_odoo_datetime(date: str) -> datetime:
    return datetime.strptime(date, "%Y-%m-%d %H:%M:%S")


def get_fixed_timestamp(current_time: datetime):
    offset = -get_seasonal_offset(datetime.now())
    return current_time + timedelta(hours=offset)


def convert_seconds_to_strtime(seconds: int):
    if seconds:
        minutes = seconds // 60
        if minutes < 60:
            return f"+{minutes}m"
        else:
            return f"+{minutes // 60}h{minutes % 60}"
    return ""
