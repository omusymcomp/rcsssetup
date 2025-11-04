import subprocess
import argparse
import sys
import os
from datetime import datetime
import getpass

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--base_dir", dest="base_dir", default=os.path.expandvars("$HOME/rcss"), 
                        help="Specify the base directory for environment setup")
    parser.add_argument("-l", "--left_team_name", dest="left_team_name", default="helios2024", 
                        choices=["custom", "HELIOS2023", "helios-base", "YuShan2023", "CYRUS",
                                 "EMPEROR", "Hermes2D", "Oxsy", "RoboCIn", "Damavand", "FRA-UNIted",
                                 "Hades2D", "ITAndroids", "The8", "R3CESBU", "robo2d","mars","aeteam", 
                                 "cyrus", "oxcy", "r2d2", "helios", "fra-united", "itandroids", "yushan2024"], help="Specify the left team name")
    parser.add_argument("-r", "--right_team_name", dest="right_team_name", default="cyrus", 
                        choices=["custom", "HELIOS2023", "helios-base", "YuShan2023", "CYRUS",
                                 "EMPEROR", "Hermes2D", "Oxsy", "RoboCIn", "Damavand", "FRA-UNIted",
                                 "Hades2D", "ITAndroids", "The8", "R3CESBU", "robo2d","mars","aeteam",
                                   "cyrus", "oxcy", "r2d2", "helios", "fra-united", "itandroids", "yushan2024"], help="Specify the right team name")
    parser.add_argument("-n", "--match_number", dest="match_number", default=3, type=int, 
                        help="Specify the number of matches")
    parser.add_argument("--is_synch_mode", action="store_true", dest="is_synch_mode", help="Specify if synch mode should be enabled")
    parser.add_argument("-y", "--team_year", dest="team_year", default="rc2024", choices=["rc2023", "rc2024"],
                    help="Specify the year of the team binaries to use (rc2023 or rc2024)")

    
    args = parser.parse_args()
    auto_match = AutoMatch(args)
    auto_match.execute_matches(args)

class AutoMatch:
    # チームごとの起動スクリプトを定義
    team_start_scripts_203 = {
        "CYRUS": "startAll",
        "FRA-UNIted": "startlocal.sh",
        # "Hermes2D": "start.sh",
        "R3CESBU": "startAll",
        "YuShan2023": "localStartAll",
        "Damavand": "localStartAll",
        "HELIOS2023": "start.sh",
        "ITAndroids": "start.sh",
        "RoboCIn": "startAll",
        "robo2d": "localStartAll",
        # "EMPEROR": "start.sh",
        "Hades2D": "localStartAll",
        "Oxsy": "startlocal",
        "The8": "startAll",
        "mars":"bins/start.sh",
        "yushan2024": "start.sh"
    }

    team_start_scripts_2024 = {
        "aeteam": "start.sh",
        "cyrus": "startAll",
        "oxcy": "startlocal",
        "r2d2": "start.sh",
        "helios": "start.sh",
        "fra-united": "start_team.sh",
        "itandroids": "start.sh",
        "mars": "start.sh",
        "yushan2024": "start.sh"
    }

    def __init__(self, args):
        now = datetime.now()
        self.formatted_date_time = now.strftime("%Y%m%d%H%M%S")
        self.log_dir = os.getenv("MATCH_LOG_DIR", f"{args.base_dir}/log_analysis/log/{self.formatted_date_time}")
        self.team_binary_dir = os.getenv("TEAM_DIR", f"{args.base_dir}/teams/rc2024")
        self.left_team_path_list = []
        self.right_team_path_list = []
        self.output_text = None

        if args.left_team_name == "custom":
            self.left_team_path_list = self.get_custom_team_path_list()
        else:
            self.left_team_path_list.append(self.get_team_path(args.left_team_name))

        if args.right_team_name == "custom":
            self.right_team_path_list = self.get_custom_team_path_list()
        else:
            self.right_team_path_list.append(self.get_team_path(args.right_team_name))

    def get_custom_team_path_list(self):
        custom_dir = self.change_home_path(f"{self.team_binary_dir}/custom")
        team_dirs = [name for name in os.listdir(custom_dir)]
        path_list = []

        for team_name in team_dirs:
            script_name = self.team_start_scripts.get(team_name, "start.sh")
            path_list.append(f"{custom_dir}/{team_name}/{script_name}")

        return path_list

    def get_team_path(self, team_name):
        team_path_base = f"{self.team_binary_dir}/{team_name}"
        
        if "rc2024" in self.team_binary_dir:
            # rc2024 用のスクリプト名マッピングを使う
            script_name = self.team_start_scripts_2024.get(team_name.lower(), "start.sh")
            return f"{team_path_base}/bin/{script_name}"
        else:
            # 通常のスクリプト名マッピングを使う
            script_name = self.team_start_scripts_2023.get(team_name, "start.sh")
            return f"{team_path_base}/{script_name}"

    def run_command(self, command):
        try:
            self.output_text = subprocess.run(command, check=True, text=True, shell=True, stdout=subprocess.PIPE).stdout
            print(self.output_text)
            print(f"Execution completed successfully: {command}\n\n")
        except subprocess.CalledProcessError as e:
            print(e.stderr)
            print(f"Error occurred with the command: {command}\n\n")
        except Exception as e:
            print(e)
            print(f"An unexpected error occurred: {command}\n\n")

    def execute_matches(self, args):
        for left_team_path in self.left_team_path_list:
            for right_team_path in self.right_team_path_list:
                for counter in range(args.match_number):
                    execute_command = f"{args.base_dir}/tools/bin/rcssserver server::auto_mode = 1 " \
                                      f"server::synch_mode = {int(args.is_synch_mode)} " \
                                      f"server::team_l_start = {left_team_path} " \
                                      f"server::team_r_start = {right_team_path} " \
                                      f"server::kick_off_wait = 50 " \
                                      f"server::half_time = 300 " \
                                      f"server::nr_normal_halfs = 2 server::nr_extra_halfs = 0 " \
                                      f"server::penalty_shoot_outs = 0 " \
                                      f"server::game_logging = 1 server::text_logging = 1 " \
                                      f"server::game_log_dir = {self.log_dir} server::text_log_dir = {self.log_dir} "
                                                                            
                    self.run_command(f"{execute_command}")
                    self.output_log(counter, left_team_path, right_team_path)

    def output_log(self, counter, left_team_path, right_team_path):
        log_dir = self.change_home_path(self.log_dir)
        left_team_name, right_team_name = self.get_team_name(left_team_path, right_team_path)

        with open(f"{log_dir}/{self.formatted_date_time}_{left_team_name}_vs_{right_team_name}_match{counter}.log", "w") as log_file:
            log_file.write(self.output_text)

    def change_home_path(self, target):
        return target.replace("$HOME", f"/home/{getpass.getuser()}") if "$HOME" in target else target

    def get_team_name(self, left_team_path, right_team_path):
        left_team_name = os.path.basename(os.path.dirname(left_team_path))
        right_team_name = os.path.basename(os.path.dirname(right_team_path))
        return left_team_name, right_team_name

if __name__ == "__main__":
    main()
