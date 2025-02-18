import datetime
from xmlrpc.client import ServerProxy, Fault
from .colors import red
from .data_manager import DataManager
from .time_functions import get_fixed_timestamp, parse_odoo_datetime, get_week_first_day


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
            exit(1)

    def get_user_employee_id(self) -> int:
        """Returns the ID of the employee linked to the user."""

        return self.execute("hr.employee", "search", [[["user_id", "=", self.uid]]])[0]

    def get_employee_attendance_state(self) -> str:
        employee = self.execute(
            "hr.employee",
            "search_read",
            [[("id", "=", self.employee_id)]],
            {"fields": ["attendance_state"]},
        )[0]

        return employee["attendance_state"]

    def add_attendance(self, attendance_time: datetime.datetime):
        """Creates a new attendance on Odoo and returns its ID."""

        if self.get_employee_attendance_state() == "checked_in":
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
        dt = datetime.datetime.date(datetime.datetime.now())
        day_start = datetime.datetime.combine(dt, datetime.datetime.min.time())
        day_end = datetime.datetime.combine(dt, datetime.datetime.max.time())
        attendances = self.execute(
            "hr.attendance",
            "search_read",
            [
                [
                    ("check_in", ">=", day_start),
                    "|",
                    ("check_out", "<=", day_end),
                    ("check_out", "=", False),
                ]
            ],
            {"fields": ["check_in", "check_out"]},
        )

        return [
            att for att in attendances if day.__str__() == att["check_in"].split()[0]
        ]

    def get_week_attendances(self):
        first_week_day = get_week_first_day()

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

    def update_last(
        self, last_att_id: int, last_action: str, attendance_time: datetime.datetime
    ):
        self.execute(
            "hr.attendance",
            "write",
            [[last_att_id], {last_action: attendance_time}],
        )
