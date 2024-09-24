import datetime
from xmlrpc.client import ServerProxy
from .data_manager import DataManager
from .time_functions import get_seasonal_offset, get_str_from_float_time


class OdooClient:
    """Client that makes the connection between the script and Odoo."""

    ATT_ACTIONS = {"entree": "sign_in", "sortie": "sign_out"}

    def __init__(self):
        self.season_offset = get_seasonal_offset(datetime.datetime.now())

        credentials = DataManager()
        self.username = credentials.get("id")
        self.pwd = credentials.get("pwd")
        self.server_url = credentials.get("server_url")
        self.db = credentials.get("db")

        self.models = self.get_models_server()

        self.uid = self.get_uid()
        self.employee_id = self.get_user_employee_id()

    def get_uid(self) -> int:
        """Get the user's ID from Odoo."""

        common = ServerProxy(f"{self.server_url}/common")
        return common.authenticate(self.db, self.username, self.pwd, {})

    def get_models_server(self) -> ServerProxy:
        """Returns the ServerProxy used to interact with Odoo's records."""

        return ServerProxy(f"{self.server_url}/object")

    def execute(self, model: str, function: str, *args):
        return self.models.execute_kw(
            self.db, self.uid, self.pwd, model, function, *args
        )

    def get_user_employee_id(self) -> int:
        """Returns the ID of the employee linked to the user."""

        return self.execute("hr.employee", "search", [[["user_id", "=", self.uid]]])[0]

    def add_attendance(self, action: str, offset: int):
        """Creates a new attendance on Odoo and returns its ID."""

        delta_offset = datetime.timedelta(minutes=offset)
        now = datetime.datetime.now() + delta_offset

        # It looks like odoo doesn't care about the hour change per season.
        attendance_time = (
            f"{now.strftime('%Y-%m-%d')} "
            + f"{str(int(now.hour) - 2).zfill(1)}:"
            + f"{now.strftime('%M:%S')}"
        )

        record_data = {
            "employee_id": self.employee_id,
            "name": attendance_time,
            "action": OdooClient.ATT_ACTIONS[action],
        }

        try:
            att_id = self.execute("hr.attendance", "create", [record_data])
        except:
            att_id = -1
        return (att_id, now)

    def get_last_x_attendance(self, limit: int):
        return self.execute(
            "hr.attendance",
            "search_read",
            [[]],
            {"fields": ["name", "action"], "limit": limit},
        )

    def get_day_attendance(self, day: datetime.date):
        attendances = self.execute(
            "hr.attendance",
            "search_read",
            [[]],
            {"fields": ["name", "action"], "limit": 20},
        )

        return [att for att in attendances if day.__str__() == att["name"].split()[0]]

    def delete(self, id: int):
        return self.execute("hr.attendance", "unlink", [[id]])

    def get_current_time(self):
        week_time = self.execute(
            "hr_timesheet_sheet.sheet",
            "search_read",
            [[["employee_id", "=", self.employee_id]]],
            {"fields": ["id", "total_attendance"], "order": "id desc", "limit": 1},
        )[0]

        # TODO Gerer l'erreur quand aucune attendance n'a ete creee.
        day_time = self.execute(
            "hr_timesheet_sheet.sheet.day",
            "search_read",
            [[["sheet_id", "=", week_time["id"]]]],
            {"fields": ["id", "total_attendance"], "order": "name desc", "limit": 1},
        )[0]

        return (
            get_str_from_float_time(day_time["total_attendance"]),
            get_str_from_float_time(week_time["total_attendance"]),
        )

    def get_week_overtime(self) -> str:
        week_id = self.execute(
            "hr_timesheet_sheet.sheet",
            "search_read",
            [[["employee_id", "=", self.employee_id]]],
            {"fields": ["id"], "order": "id desc", "limit": 1},
        )[0]["id"]

        days = self.execute(
            "hr_timesheet_sheet.sheet.day",
            "search_read",
            [[["sheet_id", "=", week_id]]],
            {
                "fields": ["id", "total_attendance"],
                "order": "name desc",
            },
        )

        overtime = 0
        for day in days:
            if day["total_attendance"] > 7:
                overtime += day["total_attendance"] - 7
        return get_str_from_float_time(overtime)
