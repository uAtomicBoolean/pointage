from datetime import date, datetime, timedelta
from .colors import red


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
        return 0
    return 1


def convert_offset_to_odoo_datetime(offset: int) -> int:
    try:
        offset = int(offset)
    except ValueError:
        try:
            raw_hour = offset.lower().replace("h", ":")
            hour = datetime.strptime(raw_hour, "%H:%M")
            full_date = datetime.combine(date.today(), hour.time())

            # Convert the fulldate to an integer offset.
            time_diff = full_date - datetime.now()
            offset = int(time_diff.total_seconds() // 60)
        except:
            print(red("Erreur dans le formatage de l'heure (ex: 12H30, 12h30, 12:30)."))
            exit(1)

    current_time = datetime.now() + timedelta(minutes=offset)
    current_time_season_fixed = get_fixed_timestamp(current_time)

    # Odoo doesn't care about the hour change per season.
    # Odoo use UTC instead of UTC+2 hence the -2 is mandatory.
    return (
        f"{current_time_season_fixed.strftime('%Y-%m-%d')} "
        + f"{str(int(current_time_season_fixed.hour) - 2).zfill(2)}:"
        + f"{current_time_season_fixed.strftime('%M:%S')}"
    )


def parse_odoo_datetime(date: str) -> datetime:
    if get_seasonal_offset(datetime.now()) == 1:
        return datetime.strptime(date, "%Y-%m-%d %H:%M:%S") + timedelta(hours=1)
    return datetime.strptime(date, "%Y-%m-%d %H:%M:%S") + timedelta(hours=2)


def get_fixed_timestamp(current_time: datetime):
    offset = get_seasonal_offset(datetime.now())
    return current_time + timedelta(hours=offset)


def convert_seconds_to_strtime(seconds: int):
    if seconds:
        minutes = seconds // 60
        if minutes < 60:
            return f"+{minutes}m"
        else:
            return f"+{minutes // 60}h{minutes % 60}"
    return ""


def get_week_first_day():
    curr_date = date.today()
    return curr_date - timedelta(days=curr_date.weekday())


def get_work_time(attendances: list[dict]) -> datetime:
    """Returns the work time in seconds."""

    total_time = timedelta(hours=0)
    for att in attendances:
        total_time += att["check_out"] - att["check_in"]

    return total_time.days * 86400 + total_time.seconds


def beautify_work_time(work_time: int) -> str:
    hours = f"{work_time // 3600}".zfill(2)
    minutes = f"{(work_time % 3600) // 60}".zfill(2)
    return f"{hours}h{minutes}"
