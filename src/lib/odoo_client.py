import datetime
from xmlrpc.client import ServerProxy, Fault
from .colors import red
from .data_manager import DataManager
from .time_functions import get_fixed_timestamp, parse_odoo_datetime


class OdooClient:
    """Client that makes the connection between the script and Odoo."""

    ATT_ACTIONS = {"entree": "sign_in", "sortie": "sign_out"}

    def __init__(self):
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
        try:
            return self.models.execute_kw(
                self.db, self.uid, self.pwd, model, function, *args
            )
        except Fault as err:
            print(red(f"Erreur dans la communication XMLRPC (code {err.faultCode})"))
            print(red(err.faultString))

    def get_user_employee_id(self) -> int:
        """Returns the ID of the employee linked to the user."""

        return self.execute("hr.employee", "search", [[["user_id", "=", self.uid]]])[0]

    def add_attendance(self, offset: int):
        """Creates a new attendance on Odoo and returns its ID."""

        current_time = datetime.datetime.now() + datetime.timedelta(minutes=offset)
        current_time_season_fixed = get_fixed_timestamp(current_time)

        # Odoo doesn't care about the hour change per season.
        attendance_time = (
            f"{current_time_season_fixed.strftime('%Y-%m-%d')} "
            + f"{str(int(current_time_season_fixed.hour) - 2).zfill(1)}:"
            + f"{current_time_season_fixed.strftime('%M:%S')}"
        )

        employee = self.execute(
            "hr.employee",
            "search_read",
            [[("id", "=", self.employee_id)]],
            {"fields": ["attendance_state"]},
        )[0]

        if employee["attendance_state"] == "checked_in":
            attendance = self.execute(
                "hr.attendance",
                "search_read",
                [[("employee_id", "=", self.employee_id), ("check_out", "=", False)]],
                {"limit": 1},
            )[0]
            self.execute(
                "hr.attendance",
                "write",
                [[attendance["id"]], {"check_out": attendance_time}],
            )
            return "Sortie", attendance_time

        self.execute(
            "hr.attendance",
            "create",
            [{"employee_id": self.employee_id, "check_in": attendance_time}],
        )
        return "Entrée", attendance_time

    def get_last_x_attendance(self, limit: int):
        return self.execute(
            "hr.attendance",
            "search_read",
            [[]],
            {"fields": ["check_in", "check_out"], "limit": limit // 2},
        )

    def get_day_attendance(self, day: datetime.date):
        attendances = self.execute(
            "hr.attendance",
            "search_read",
            [[]],
            {"fields": ["check_in", "check_out"], "limit": 20},
        )

        return [
            att for att in attendances if day.__str__() == att["check_in"].split()[0]
        ]

    def delete(self, id: int):
        return self.execute("hr.attendance", "unlink", [[id]])

    def get_week_attendances(self):
        curr_date = datetime.date.today()
        first_week_day = curr_date - datetime.timedelta(days=curr_date.weekday())
        first_week_day = first_week_day.strftime("%Y-%m-%d %H:%M:%S")

        attendances = self.execute(
            "hr.attendance",
            "search_read",
            [[["check_in", ">=", first_week_day]]],
            {"fields": ["check_in", "check_out"], "limit": 50},
        )

        for att in attendances:
            if not att["check_in"]:
                return []

            att["check_in"] = get_fixed_timestamp(parse_odoo_datetime(att["check_in"]))
            if att["check_out"]:
                att["check_out"] = get_fixed_timestamp(
                    parse_odoo_datetime(att["check_out"])
                )

        return attendances
