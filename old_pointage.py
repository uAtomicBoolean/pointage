#!/usr/bin/python3

import argparse
import datetime
from xmlrpc.client import ServerProxy


URL = "https://erp.teicee.fr/xmlrpc/2"
DB = "teicee"
USERNAME = ""
PASSWORD = ""

ATT_ACTIONS = {
    "entree": "sign_in",
    "sortie": "sign_out",
}


def get_uid() -> int:
    """Get the user's ID from Odoo."""

    common = ServerProxy(f"{URL}/common")
    return common.authenticate(DB, USERNAME, PASSWORD, {})


def get_models_server() -> ServerProxy:
    """Returns the ServerProxy used to interact with Odoo's records."""

    return ServerProxy(f"{URL}/object")


def get_user_employee_id(uid: int, models: ServerProxy) -> int:
    """Returns the ID of the employee linked to the user."""

    return models.execute_kw(
        DB, uid, PASSWORD, "hr.employee", "search", [[["user_id", "=", uid]]]
    )[0]


def add_attendance(
    uid: int, employee_id: int, models: ServerProxy, action: str, offset: int
):
    """Creates a new attendance on Odoo and returns its ID."""

    delta_offset = datetime.timedelta(minutes=offset)
    date = datetime.datetime.now() + delta_offset
    attendance_time = f"{date.strftime('%Y-%m-%d')} {str(int(date.hour) - 1).zfill(1)}:{date.strftime('%M:%S')}"
    record_data = {
        "employee_id": employee_id,
        "name": attendance_time,
        "action": ATT_ACTIONS[action],
    }

    try:
        att_id = models.execute_kw(
            DB, uid, PASSWORD, "hr.attendance", "create", [record_data]
        )
    except:
        att_id = -1
    return (att_id, date)


def get_last_attendance(uid: int, models: ServerProxy):
    last_att = models.execute_kw(
        DB,
        uid,
        PASSWORD,
        "hr.attendance",
        "search_read",
        [[]],
        {"fields": ["name", "action"], "limit": 1},
    )[0]

    date = datetime.datetime.strptime(last_att["name"], "%Y-%m-%d %H:%M:%S")
    last_att["name"] = date + datetime.timedelta(hours=1)

    return last_att


def get_current_time(uid: int, employee_id: int, models: ServerProxy):
    last_timesheet = models.execute_kw(
        DB,
        uid,
        PASSWORD,
        "hr_timesheet_sheet.sheet",
        "search_read",
        [[["employee_id", "=", employee_id]]],
        {"fields": ["id"], "limit": 1},
    )[0]

    current_day = models.execute_kw(
        DB,
        uid,
        PASSWORD,
        "hr_timesheet_sheet.sheet.day",
        "search_read",
        [[["sheet_id", "=", last_timesheet["id"]]]],
        {"order": "name desc", "limit": 1},
    )[0]

    str_time = str(current_day["total_difference"]).split(".")

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


if __name__ == "__main__":
    if not USERNAME or not PASSWORD:
        print("Veuillez mettre vos identifiants dans le script.")
        import sys

        sys.exit(1)

    parser = argparse.ArgumentParser(
        prog="pointeur",
        description="Ajoute une entree ou une sortie au pointage de Odoo.",
    )

    parser.add_argument(
        "action",
        help="L'action à effectuer.",
        choices=["entree", "sortie", "last", "time"],
    )
    parser.add_argument(
        "-o",
        "--offset",
        help="Décalage en minutes par rapport à l'heure actuelle (ex: 5, -3).",
        type=int,
        required=False,
    )

    args = parser.parse_args()

    offset = 0 if not args.offset else args.offset

    MODELS = get_models_server()
    UID = get_uid()
    EMPLOYEE_ID = get_user_employee_id(UID, MODELS)

    if args.action in ["entree", "sortie"]:
        attendance_id, date_pointage = add_attendance(
            UID, EMPLOYEE_ID, MODELS, args.action, offset
        )
        if attendance_id == -1:
            print(f"Erreur lors de la création du pointage (action: {args.action}).")
            print(
                "Vérifiez si vous n'avez pas déjà créer un pointage avec cette action."
            )
        else:
            print(f"Pointage créé (id: {attendance_id}) pour l'heure {date_pointage}")
    elif args.action == "last":
        last_att = get_last_attendance(UID, MODELS)
        action_name = [
            act for act, o_act in ATT_ACTIONS.items() if o_act == last_att["action"]
        ][0]
        print(f"Dernier pointage : {action_name} à {last_att['name']}")
    elif args.action == "time":
        current_time = get_current_time(UID, EMPLOYEE_ID, MODELS)
        print(f"Journée actuelle : {current_time}")
