import argparse
import getpass
import os
import re
import subprocess
import sys
from datetime import datetime


SCRIPT_SETTINGS = {
    "rc2022": {
        "script_map": {},
        "use_bin": False,
        "use_lower_key": False,
    },
    "rc2023": {
        "script_map": {
            "CYRUS": "startAll",
            "FRA-UNIted": "startlocal.sh",
            "R3CESBU": "startAll",
            "YuShan": "localStartAll",
            "YuShan2023": "localStartAll",
            "Damavand": "localStartAll",
            "HELIOS": "start.sh",
            "HELIOS2023": "start.sh",
            "ITAndroids": "start.sh",
            "RoboCIn": "startAll",
            "robo2d": "localStartAll",
            "Hades2D": "localStartAll",
            "Oxsy": "startlocal",
            "The8": "startAll",
            "mars": "bins/start.sh",
            "yushan2024": "start.sh",
        },
        "use_bin": False,
        "use_lower_key": False,
    },
    "rc2024": {
        "script_map": {
            "aeteam": "start.sh",
            "cyrus": "startAll",
            "oxsy": "startlocal",
            "r2d2": "start.sh",
            "helios": "start.sh",
            "fra-united": "start_team.sh",
            "itandroids": "start.sh",
            "mars": "start.sh",
            "yushan2024": "start.sh",
        },
        "use_bin": True,
        "use_lower_key": True,
    },
    "rc2025": {
        "script_map": {
            "helios2025": "start.sh",
            "yushan2025": "startAll.sh",
            "fra-united": "start_team.sh",
            "itandroids": "start.sh",
            "oxsy": "startlocal",
            "robocin": "startAll",
            "robotech": "start.sh",
            "sirlab": "start.sh",
            "srbiau2d": "start.sh",
            "titasdarobotica": "localStartAll",
        },
        "use_bin": False,
        "use_lower_key": True,
    },
}

SPECIAL_TEAM_ALIASES = {
    "hrlios-base": "helios-base",
}


def resolve_team_root(base_dir):
    team_dir_env = os.getenv("TEAM_DIR")
    if not team_dir_env:
        return os.path.join(base_dir, "teams")

    resolved_dir = change_home_path(team_dir_env)
    base_name = os.path.basename(os.path.normpath(resolved_dir))
    if re.fullmatch(r"rc20\d{2}", base_name):
        return os.path.dirname(resolved_dir)
    return resolved_dir


def list_installed_teams(team_root):
    installed = {}
    for year_dir in sorted(SCRIPT_SETTINGS):
        year_root = os.path.join(team_root, year_dir)
        if not os.path.isdir(year_root):
            continue

        for team_name in sorted(os.listdir(year_root)):
            team_dir = os.path.join(year_root, team_name)
            if not os.path.isdir(team_dir):
                continue
            installed[team_name] = (year_dir, team_dir)

    return installed


def split_team_name_and_year(team_name):
    matched = re.match(r"^(.*?)(20\d{2})$", team_name)
    if not matched:
        return team_name, None
    return matched.group(1), matched.group(2)


def get_script_name(year_dir, team_name):
    settings = SCRIPT_SETTINGS[year_dir]
    base_name, _ = split_team_name_and_year(team_name)
    lookup_candidates = [team_name]
    if base_name and base_name != team_name:
        lookup_candidates.append(base_name)

    for lookup_name in lookup_candidates:
        if settings["use_lower_key"]:
            lookup_name = lookup_name.lower()
        if lookup_name in settings["script_map"]:
            return settings["script_map"][lookup_name]

    return "start.sh"


def build_parser(team_choices):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-d",
        "--base_dir",
        dest="base_dir",
        default=os.path.expandvars("$HOME/rcss"),
        help="Specify the base directory for environment setup",
    )
    parser.add_argument(
        "-l",
        "--left_team_name",
        dest="left_team_name",
        default="HELIOS2025",
        help="Specify the left team directory name",
    )
    parser.add_argument(
        "-r",
        "--right_team_name",
        dest="right_team_name",
        default="YuShan2025",
        help="Specify the right team directory name",
    )
    parser.add_argument(
        "-n",
        "--match_number",
        dest="match_number",
        default=3,
        type=int,
        help="Specify the number of matches",
    )
    parser.add_argument(
        "--is_synch_mode",
        action="store_true",
        dest="is_synch_mode",
        help="Specify if synch mode should be enabled",
    )
    parser.add_argument(
        "-y",
        "--team_year",
        dest="team_year",
        default="rc2025",
        choices=sorted(SCRIPT_SETTINGS),
        help="Specify the year used only when selecting custom teams",
    )
    parser.epilog = (
        "Installed team names: "
        + (", ".join(team_choices) if team_choices else "none found")
    )
    return parser


def main():
    base_parser = argparse.ArgumentParser(add_help=False)
    base_parser.add_argument("-d", "--base_dir", dest="base_dir", default=os.path.expandvars("$HOME/rcss"))
    preliminary_args, _ = base_parser.parse_known_args()

    team_root = resolve_team_root(preliminary_args.base_dir)
    installed_teams = list_installed_teams(team_root)
    team_choices = ["custom", "helios-base"] + sorted(installed_teams)

    parser = build_parser(team_choices)
    args = parser.parse_args()

    auto_match = AutoMatch(args, installed_teams, team_root)
    auto_match.execute_matches(args)


class AutoMatch:
    def __init__(self, args, installed_teams, team_root):
        now = datetime.now()
        self.formatted_date_time = now.strftime("%Y%m%d%H%M%S")
        self.base_dir = args.base_dir
        self.team_root = team_root
        self.log_dir = os.getenv("MATCH_LOG_DIR", f"{args.base_dir}/log_analysis/log/{self.formatted_date_time}")
        self.default_custom_year = args.team_year
        self.installed_teams = installed_teams
        self.left_team_path_list = []
        self.right_team_path_list = []
        self.output_text = None

        left_team_name = self.normalize_team_name(args.left_team_name)
        right_team_name = self.normalize_team_name(args.right_team_name)

        self.left_team_path_list = self.resolve_team_selection(left_team_name)
        self.right_team_path_list = self.resolve_team_selection(right_team_name)

    def normalize_team_name(self, team_name):
        return SPECIAL_TEAM_ALIASES.get(team_name, team_name)

    def resolve_team_selection(self, team_name):
        if team_name == "custom":
            return self.get_custom_team_path_list()
        return [self.get_team_path(team_name)]

    def get_custom_team_path_list(self):
        custom_dir = change_home_path(os.path.join(self.team_root, self.default_custom_year, "custom"))
        if not os.path.isdir(custom_dir):
            print(f"Custom team directory not found: {custom_dir}")
            return []

        path_list = []
        for team_name in sorted(os.listdir(custom_dir)):
            team_dir = os.path.join(custom_dir, team_name)
            if not os.path.isdir(team_dir):
                continue

            script_name = get_script_name(self.default_custom_year, team_name)
            path_list.append(self.build_team_script_path(team_dir, self.default_custom_year, script_name))

        return path_list

    def get_team_path(self, team_name):
        if team_name == "helios-base":
            helios_base_root = os.path.join(self.base_dir, "teams", "base_team", "helios-base")
            src_start = os.path.join(helios_base_root, "src", "start.sh")
            root_start = os.path.join(helios_base_root, "start.sh")
            if os.path.exists(src_start):
                return src_start
            return root_start

        if team_name not in self.installed_teams:
            available = ", ".join(sorted(self.installed_teams))
            raise ValueError(f"Unknown team '{team_name}'. Installed teams: {available}")

        year_dir, team_dir = self.installed_teams[team_name]
        script_name = get_script_name(year_dir, team_name)
        return self.build_team_script_path(team_dir, year_dir, script_name)

    def build_team_script_path(self, team_dir, year_dir, script_name):
        settings = SCRIPT_SETTINGS[year_dir]
        if settings["use_bin"]:
            return os.path.join(team_dir, "bin", script_name)
        return os.path.join(team_dir, script_name)

    def run_command(self, command):
        try:
            self.output_text = subprocess.run(
                command,
                check=True,
                text=True,
                shell=True,
                stdout=subprocess.PIPE,
            ).stdout
            print(self.output_text)
            print(f"Execution completed successfully: {command}\n")
        except subprocess.CalledProcessError as e:
            print(e.stderr)
            print(f"Error occurred with the command: {command}\n")
        except Exception as e:
            print(e)
            print(f"An unexpected error occurred: {command}\n")

    def execute_matches(self, args):
        for left_team_path in self.left_team_path_list:
            for right_team_path in self.right_team_path_list:
                for counter in range(args.match_number):
                    execute_command = (
                        f"{args.base_dir}/tools/bin/rcssserver server::auto_mode = 1 "
                        f"server::synch_mode = {int(args.is_synch_mode)} "
                        f"server::team_l_start = {left_team_path} "
                        f"server::team_r_start = {right_team_path} "
                        f"server::kick_off_wait = 50 "
                        f"server::half_time = 300 "
                        f"server::nr_normal_halfs = 2 server::nr_extra_halfs = 0 "
                        f"server::penalty_shoot_outs = 0 "
                        f"server::game_logging = 1 server::text_logging = 1 "
                        f"server::game_log_dir = {self.log_dir} server::text_log_dir = {self.log_dir} "
                    )

                    self.run_command(execute_command)
                    self.output_log(counter, left_team_path, right_team_path)

    def output_log(self, counter, left_team_path, right_team_path):
        log_dir = change_home_path(self.log_dir)
        os.makedirs(log_dir, exist_ok=True)
        left_team_name, right_team_name = self.get_team_name(left_team_path, right_team_path)

        with open(
            f"{log_dir}/{self.formatted_date_time}_{left_team_name}_vs_{right_team_name}_match{counter}.log",
            "w",
        ) as log_file:
            log_file.write(self.output_text or "")

    def get_team_name(self, left_team_path, right_team_path):
        left_team_name = os.path.basename(os.path.dirname(left_team_path))
        right_team_name = os.path.basename(os.path.dirname(right_team_path))
        return left_team_name, right_team_name


def change_home_path(target):
    return target.replace("$HOME", f"/home/{getpass.getuser()}") if "$HOME" in target else target


if __name__ == "__main__":
    try:
        main()
    except ValueError as exc:
        print(exc)
        sys.exit(1)
