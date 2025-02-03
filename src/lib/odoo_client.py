import datetime
from xmlrpc.client import ServerProxy
from .data_manager import DataManager
from .time_functions import get_fixed_timestamp


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
        return self.models.execute_kw(
            self.db, self.uid, self.pwd, model, function, *args
        )

    def get_user_employee_id(self) -> int:
        """Returns the ID of the employee linked to the user."""

        return self.execute("hr.employee", "search", [[["user_id", "=", self.uid]]])[0]

    def add_attendance(self, action: str, offset: int):
        """Creates a new attendance on Odoo and returns its ID."""

        current_time = datetime.datetime.now() + datetime.timedelta(minutes=offset)
        current_time_season_fixed = get_fixed_timestamp(current_time)

        # It looks like odoo doesn't care about the hour change per season.
        attendance_time = (
            f"{current_time_season_fixed.strftime('%Y-%m-%d')} "
            + f"{str(int(current_time_season_fixed.hour) - 2).zfill(1)}:"
            + f"{current_time_season_fixed.strftime('%M:%S')}"
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
        return (att_id, current_time)

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

    def get_current_time(self):
        curr_date = datetime.date.today()
        first_week_day = curr_date - datetime.timedelta(days=curr_date.weekday())
        last_week_day = first_week_day + datetime.timedelta(days=4)

        first_week_day = first_week_day.strftime("%Y-%m-%d %H:%M:%S")
        last_week_day = last_week_day.strftime("%Y-%m-%d %H:%M:%S")

        attendances = self.execute(
            "hr.attendance",
            "search_read",
            [
                [
                    ["check_in", ">=", first_week_day],
                    "|",
                    ["check_out", "<=", last_week_day],
                    ["check_out", "=", False],
                ]
            ],
            {"fields": ["check_in", "check_out"], "limit": 2},
        )

        for att in attendances:
            if not att["check_in"]:
                return []

            att["check_in"] = get_fixed_timestamp(
                datetime.datetime.strptime(att["check_in"], "%Y-%m-%d %H:%M:%S")
            )
            if att["check_out"]:
                att["check_out"] = get_fixed_timestamp(
                    datetime.datetime.strptime(att["check_out"], "%Y-%m-%d %H:%M:%S")
                )

        return attendances

        """ week_time = self.execute(
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
        ) """
