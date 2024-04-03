import datetime
from xmlrpc.client import ServerProxy
from .credentials_manager import CredentialsManager
from .utils import get_season


class OdooClient:
    """Client that makes the connection between the script and Odoo."""

    URL = "https://erp.teicee.fr/xmlrpc/2"
    DB = "teicee"

    ATT_ACTIONS = {"entree": "sign_in", "sortie": "sign_out"}

    def __init__(self):
        if get_season(datetime.datetime.now()) in ["spring", "summer"]:
            self.season_offset = -2
        else:
            self.season_offset = -1

        credentials = CredentialsManager()
        self.username = credentials.get("id")
        self.pwd = credentials.get("pwd")

        self.models = self.get_models_server()

        self.uid = self.get_uid()
        self.employee_id = self.get_user_employee_id()

    def get_uid(self) -> int:
        """Get the user's ID from Odoo."""

        common = ServerProxy(f"{OdooClient.URL}/common")
        return common.authenticate(OdooClient.DB, self.username, self.pwd, {})

    def get_models_server(self) -> ServerProxy:
        """Returns the ServerProxy used to interact with Odoo's records."""

        return ServerProxy(f"{OdooClient.URL}/object")

    def get_user_employee_id(self) -> int:
        """Returns the ID of the employee linked to the user."""

        return self.models.execute_kw(
            OdooClient.DB,
            self.uid,
            self.pwd,
            "hr.employee",
            "search",
            [[["user_id", "=", self.uid]]],
        )[0]

    def add_attendance(self, action: str, offset: int):
        """Creates a new attendance on Odoo and returns its ID."""

        delta_offset = datetime.timedelta(minutes=offset)
        now = datetime.datetime.now() + delta_offset

        attendance_time = (
            f"{now.strftime('%Y-%m-%d')} "
            + f"{str(int(now.hour) + self.season_offset).zfill(1)}:"
            + f"{now.strftime('%M:%S')}"
        )

        record_data = {
            "employee_id": self.employee_id,
            "name": attendance_time,
            "action": OdooClient.ATT_ACTIONS[action],
        }

        try:
            att_id = self.models.execute_kw(
                OdooClient.DB,
                self.uid,
                self.pwd,
                "hr.attendance",
                "create",
                [record_data],
            )
        except:
            att_id = -1
        return (att_id, now)

    def get_last_x_attendance(self, limit: int):
        last_atts = self.models.execute_kw(
            OdooClient.DB,
            self.uid,
            self.pwd,
            "hr.attendance",
            "search_read",
            [[]],
            {"fields": ["name", "action"], "limit": limit},
        )

        return last_atts

    def get_current_time(self, get_week: bool = False):
        last_timesheet = self.models.execute_kw(
            OdooClient.DB,
            self.uid,
            self.pwd,
            "hr_timesheet_sheet.sheet",
            "search_read",
            [[["employee_id", "=", self.employee_id]]],
            {"fields": ["id", "total_difference"], "limit": 1},
        )[0]

        if not get_week:
            current_time = self.models.execute_kw(
                OdooClient.DB,
                self.uid,
                self.pwd,
                "hr_timesheet_sheet.sheet.day",
                "search_read",
                [[["sheet_id", "=", last_timesheet["id"]]]],
                {"order": "name desc", "limit": 1},
            )[0]
        else:
            current_time = last_timesheet

        str_time = str(current_time["total_difference"]).split(".")

        # Force the minutes to be 2 a digits number.
        # necessary to avoid an error where the str_minutes is only '9' instead
        # of '90' hence resulting in a converted time of 5 minutes instead of 50 minutes.
        str_minutes = str_time[1]
        if len(str_minutes) < 2:
            str_minutes += "0"

        # The minutes from Odoo are not in minutes but are in percent (0 to 100).
        # Hence we need to convert them to minutes.
        minutes = ((60 * int(str_minutes)) // 100) + 1

        return f"{str_time[0]}h{str(minutes).zfill(2)}"
