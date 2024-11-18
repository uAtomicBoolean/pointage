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


def get_fixed_timestamp(timestamp: str):
    offset = -get_seasonal_offset(datetime.now())
    return date + timedelta(hours=offset)


def get_str_from_float_time(worked_hours: float) -> str:
    """Build a string of the time worked from a timesheet."""

    if worked_hours == 0:
        return "0h"

    str_time = str(worked_hours).split(".")

    # Force the minutes to be 2 a digits number.
    # necessary to avoid an error where the str_minutes is only '9' instead
    # of '90' hence resulting in a converted time of 5 minutes instead of 50 minutes.
    str_minutes = str_time[1]
    if len(str_minutes) < 2:
        str_minutes += "0"
    elif len(str_minutes) > 2:
        reduce_factor = 10 ** (len(str_minutes) - 2)
        str_minutes = int(int(str_minutes) / reduce_factor)

    # The minutes from Odoo are not in minutes but are in percent (0 to 100).
    # Hence we need to convert them to minutes.
    minutes = ((60 * int(str_minutes)) // 100) + 1

    return f"{str_time[0]}h{str(minutes).zfill(2)}"


def convert_seconds_to_strtime(seconds: int):
    if seconds:
        minutes = seconds // 60
        if minutes < 60:
            return f"+{minutes}m"
        else:
            return f"+{minutes // 60}h{minutes % 60}"
    return ""
