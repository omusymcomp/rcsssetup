import subprocess
import argparse
import sys
import os
import getpass
import gdown
import shutil

def main():
    # Initialize Git LFS globally
    subprocess.run("git lfs install --skip-repo", check=True, shell=True)
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--base_dir", dest="base_dir", default=os.path.expandvars("$HOME/rcss"), help="Specify the base directory for environment setup")
    parser.add_argument("-t", "--install_target", dest="install_target", default="all",
                        choices=["all", "minisetup", "tools", "librcsc", "rcssserver", "soccerwindow2",
                                 "rcssmonitor", "fedit2", "helios_base", "loganalyzer3", "teams"],
                        help="Specify the installation target. 'all' installs everything, 'minisetup' installs the minimal setup required for execution, and specific tools or teams are installed if specified.")
    parser.add_argument("-j", "--jobs", type=int, dest="jobs", help="Specify the number of jobs to run simultaneously during compilation (make -j option)")
    parser.add_argument("--upgrade_packages", action="store_true", dest="upgrade_packages", help="Specify if package updates should be performed before compiling")
    parser.add_argument("--is_installation_of_essential_packages", action="store_true", dest="is_installation_of_essential_packages",
                        help="Specify if essential packages should be installed before compilation")
    parser.add_argument("--add_environment_variable", action="store_true", dest="add_environment_variable", help="Specify if environment variables should be added. Required during the initial setup.")
    args = parser.parse_args()

    setup_tools = SetupTools(args)

    setup_tools.upgrade_packages()  
    setup_tools.install_essential_packages()  
    setup_tools.add_environment_variables()

    setup_teams = SetupTeams(args)

    if args.install_target == "all":
        setup_tools.install_librcsc()
        setup_tools.install_rcssserver()
        setup_tools.install_soccerwindow2()
        setup_tools.install_rcssmonitor()
        # setup_tools.install_fedit2()
        setup_tools.install_loganalyzer3()
        setup_teams.install_teams()
        setup_teams.install_2024_teams()
        setup_teams.install_helios_base()
        setup_teams.replace_username()
        setup_teams.add_execution_permission()
    elif args.install_target == "minisetup":
        setup_tools.install_librcsc()
        setup_tools.install_rcssserver()
        setup_tools.install_soccerwindow2()
        setup_teams.install_helios_base()
    elif args.install_target == "tools":
        setup_tools.install_librcsc()
        setup_tools.install_rcssserver()
        setup_tools.install_soccerwindow2()
        setup_tools.install_rcssmonitor()
        # setup_tools.install_fedit2()
        setup_tools.install_loganalyzer3()
    elif args.install_target == "teams":
        setup_teams.install_teams()
        setup_teams.install_2024_teams()
        setup_teams.replace_username()
        setup_teams.add_execution_permission()
    else:
        # Call the method corresponding to the specified install target
        called_method = getattr(setup_tools, f"install_{args.install_target}")
        called_method()


class SetupTools:
    def __init__(self, args):
        self.base_dir = args.base_dir
        self.tools_dir = os.path.join(self.base_dir, "tools")
        self.configure_for_tools_dir = os.path.join(self.base_dir, "tools")
        self.jobs = args.jobs
        self.make_command = "make"
        if self.jobs:
            self.make_command += f" -j {self.jobs}"

    def run_command(self, command, cwd=None):
        try:
            # Be careful with shell=True, as it can lead to OS command injection
            # Since this is currently used for personal purposes, it shouldn't be an issue
            result = subprocess.run(
                command,
                check=True,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=True,
                cwd=cwd
            )
            print(result.stdout)
            # Determine the absolute path of the current working directory
            current_dir = os.path.abspath(cwd) if cwd else os.getcwd()
            print(f"Execution completed successfully: {current_dir} {command}\n")
        except subprocess.CalledProcessError as e:
            # When the command returns an error
            print(f"Command '{command}' failed with return code {e.returncode}")
            print(f"stdout:\n{e.stdout}")
            print(f"stderr:\n{e.stderr}")
            sys.exit(1)
        except Exception as e:
            # Other exceptions
            print(f"An unexpected error occurred while running command: {command}")
            print(str(e))
            sys.exit(1)

    def upgrade_packages(self):
        self.run_command("sudo apt update -y")
        self.run_command("sudo apt upgrade -y")

    def install_essential_packages(self):
        # Install the essential packages for execution
        self.run_command("sudo apt-get install -y build-essential autoconf automake libtool")
        self.run_command("sudo apt-get install -y flex bison libboost-all-dev")
        self.run_command("sudo apt-get install -y qtbase5-dev qt5-qmake libfontconfig1-dev libaudio-dev")
        self.run_command("sudo apt-get install -y libxt-dev libglib2.0-dev libxi-dev libxrender-dev")
        self.run_command("sudo apt-get install -y git-lfs wget xz-utils findutils")
        self.run_command("git lfs install")

    def add_environment_variables(self):
        # Paths to the shell configuration files
        bashrc_path = os.path.expanduser("~/.bashrc")
        profile_path = os.path.expanduser("~/.profile")

        # Environment variable lines to add
        ld_library_line = 'export LD_LIBRARY_PATH=$HOME/rcss/tools/lib:$LD_LIBRARY_PATH'
        path_line = 'export PATH=$HOME/rcss/tools/bin:$PATH'
        rcssmonitor_line = 'export RCSSMONITOR=sswindow2'

        # Function to append a line if it's not already present
        def append_if_not_present(file_path, line):
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                if line not in content:
                    with open(file_path, 'a') as f:
                        f.write('\n' + line + '\n')
                    print(f"Added line to {file_path}: {line}")
                else:
                    print(f"Line already exists in {file_path}: {line}")
            except Exception as e:
                print(f"Error while updating {file_path}: {e}")
                sys.exit(1)

        # Add the environment variables
        append_if_not_present(bashrc_path, ld_library_line)
        append_if_not_present(bashrc_path, path_line)
        append_if_not_present(bashrc_path, rcssmonitor_line)
        append_if_not_present(profile_path, path_line)

    def install_librcsc(self):
        # Compile librcsc
        os.makedirs(self.configure_for_tools_dir, exist_ok=True)
        if not os.path.exists(os.path.join(self.tools_dir, "librcsc")):
            self.run_command("git clone -b develop https://github.com/helios-base/librcsc.git", cwd=self.tools_dir)
            # Obtain Git LFS objects
            self.run_command("git lfs pull", cwd=os.path.join(self.tools_dir, "librcsc"))
        else:
            print(f"{self.tools_dir}/librcsc exists, skipping git clone")
        librcsc_dir = os.path.join(self.tools_dir, "librcsc")
        self.run_command("./bootstrap", cwd=librcsc_dir)
        self.run_command(f"./configure --prefix={self.configure_for_tools_dir}", cwd=librcsc_dir)
        self.run_command(self.make_command, cwd=librcsc_dir)
        self.run_command("make install", cwd=librcsc_dir)

    def install_rcssserver(self):
        # Compile rcssserver
        os.makedirs(self.configure_for_tools_dir, exist_ok=True)
        if not os.path.exists(os.path.join(self.tools_dir, "rcssserver")):
            self.run_command("git clone -b develop https://github.com/rcsoccersim/rcssserver.git", cwd=self.tools_dir)
            # Obtain Git LFS objects
            self.run_command("git lfs pull", cwd=os.path.join(self.tools_dir, "rcssserver"))
        else:
            print(f"{self.tools_dir}/rcssserver exists, skipping git clone")
        rcssserver_dir = os.path.join(self.tools_dir, "rcssserver")
        self.run_command("./bootstrap", cwd=rcssserver_dir)
        self.run_command(f"./configure --prefix={self.configure_for_tools_dir}", cwd=rcssserver_dir)
        self.run_command(self.make_command, cwd=rcssserver_dir)
        self.run_command("make install", cwd=rcssserver_dir)

    def install_soccerwindow2(self):
        # Compile soccerwindow2
        os.makedirs(self.configure_for_tools_dir, exist_ok=True)
        if not os.path.exists(os.path.join(self.tools_dir, "soccerwindow2")):
            self.run_command("git clone -b develop https://github.com/helios-base/soccerwindow2.git", cwd=self.tools_dir)
            # Obtain Git LFS objects
            self.run_command("git lfs pull", cwd=os.path.join(self.tools_dir, "soccerwindow2"))
        else:
            print(f"{self.tools_dir}/soccerwindow2 exists, skipping git clone")
        soccerwindow2_dir = os.path.join(self.tools_dir, "soccerwindow2")
        self.run_command("./bootstrap", cwd=soccerwindow2_dir)
        self.run_command(f"./configure --prefix={self.configure_for_tools_dir} --with-librcsc={self.configure_for_tools_dir}", cwd=soccerwindow2_dir)
        self.run_command(self.make_command, cwd=soccerwindow2_dir)
        self.run_command("make install", cwd=soccerwindow2_dir)

    def install_rcssmonitor(self):
        # Compile rcssmonitor
        os.makedirs(self.configure_for_tools_dir, exist_ok=True)
        if not os.path.exists(os.path.join(self.tools_dir, "rcssmonitor")):
            self.run_command("git clone -b develop https://github.com/rcsoccersim/rcssmonitor.git", cwd=self.tools_dir)
            # Obtain Git LFS objects
            self.run_command("git lfs pull", cwd=os.path.join(self.tools_dir, "rcssmonitor"))
        else:
            print(f"{self.tools_dir}/rcssmonitor exists, skipping git clone")
        rcssmonitor_dir = os.path.join(self.tools_dir, "rcssmonitor")
        self.run_command("./bootstrap", cwd=rcssmonitor_dir)
        self.run_command(f"./configure --prefix={self.configure_for_tools_dir} --with-librcsc={self.configure_for_tools_dir}", cwd=rcssmonitor_dir)
        self.run_command(self.make_command, cwd=rcssmonitor_dir)
        self.run_command("make install", cwd=rcssmonitor_dir)

    def install_fedit2(self):
        # Compile fedit2
        os.makedirs(self.configure_for_tools_dir, exist_ok=True)
        if not os.path.exists(os.path.join(self.tools_dir, "fedit2")):
            self.run_command("git clone -b develop https://github.com/helios-base/fedit2.git", cwd=self.tools_dir)
            # Obtain Git LFS objects
            self.run_command("git lfs pull", cwd=os.path.join(self.tools_dir, "fedit2"))
        else:
            print(f"{self.tools_dir}/fedit2 exists, skipping git clone")
        fedit2_dir = os.path.join(self.tools_dir, "fedit2")
        self.run_command("./bootstrap", cwd=fedit2_dir)
        self.run_command(f"./configure --prefix={self.configure_for_tools_dir} --with-librcsc={self.configure_for_tools_dir}", cwd=fedit2_dir)
        self.run_command(self.make_command, cwd=fedit2_dir)
        self.run_command("make install", cwd=fedit2_dir)

    def install_loganalyzer3(self):
        # Compile loganalyzer3
        os.makedirs(self.configure_for_tools_dir, exist_ok=True)
        if not os.path.exists(os.path.join(self.tools_dir, "loganalyzer3")):
            self.run_command("git clone https://github.com/opusymcomp/loganalyzer3.git", cwd=self.tools_dir)
            # Obtain Git LFS objects
            self.run_command("git lfs pull", cwd=os.path.join(self.tools_dir, "loganalyzer3"))
        else:
            print(f"{self.tools_dir}/loganalyzer3 exists, skipping git clone")


class SetupTeams:
    def __init__(self, args):
        # Dynamically get the username of the executor and construct the path
        #username = os.getlogin()
        username = getpass.getuser()
        self.base_dir = args.base_dir
        self.teams_dir = os.path.join(self.base_dir, "teams")
        self.user_teams_dir = os.path.join(self.base_dir, "teams")
        self.base_team_dir = os.path.join(self.base_dir, "teams", "base_team")
        self.rc2024_dir = os.path.join(self.base_dir, "teams", "rc2024")
        self.rc2023_dir = os.path.join(self.base_dir, "teams", "rc2023")
        self.rc2022_dir = os.path.join(self.base_dir, "teams", "rc2022")
        self.rcsssetup_teams_dir = f"/home/{username}/rcsssetup/teams"
        self.configure_for_teams_dir = self.base_team_dir
        self.jobs = args.jobs
        self.make_command = "make"
        if self.jobs:
            self.make_command += f" -j {self.jobs}"

    def run_command(self, command, cwd=None):
        try:
            # Be careful with shell=True, as it can lead to OS command injection
            # Since this is currently used for personal purposes, it shouldn't be an issue
            result = subprocess.run(
                command,
                check=True,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=True,
                cwd=cwd
            )
            print(result.stdout)
            # Determine the current working directory
            current_dir = cwd if cwd else os.getcwd()
            print(f"Execution completed successfully: {current_dir} {command}\n")
        except subprocess.CalledProcessError as e:
            # When the command returns an error
            print(f"Command '{command}' failed with return code {e.returncode}")
            print(f"stdout:\n{e.stdout}")
            print(f"stderr:\n{e.stderr}")
            sys.exit(1)
        except Exception as e:
            # Other exceptions
            print(f"An unexpected error occurred while running command: {command}")
            print(str(e))
            sys.exit(1)

    def install_teams(self):
        os.makedirs(self.rc2023_dir, exist_ok=True)
        if not os.path.exists(os.path.join(self.rc2023_dir, "HELIOS2023")):
            # Download all team files from the specified URL
            download_url = "https://archive.robocup.info/Soccer/Simulation/2D/binaries/RoboCup/2023/Day4/"
            # Use wget to recursively download all files
            self.run_command(f"wget -r -np -nH --cut-dirs=7 -R 'index.html*, robots.txt' {download_url}", cwd=self.rc2023_dir)
            self.run_command(f"find {self.teams_dir} -name '*.tar.gz' -exec tar -xzvf '{{}}' -C {self.rc2023_dir} ';'", cwd=self.rc2023_dir)
            self.run_command(f"find {self.teams_dir} -name '*.tar.xz' -exec tar -xJvf '{{}}' -C {self.rc2023_dir} ';'", cwd=self.rc2023_dir)
            self.run_command(f"find {self.teams_dir} -name '*.tar.gz' -delete", cwd=self.rc2023_dir)
            self.run_command(f"find {self.teams_dir} -name '*.tar.xz' -delete", cwd=self.rc2023_dir)
            self.run_command(f"cp -r {self.rcsssetup_teams_dir}/. {self.teams_dir}/")
        else:
            print(f"{self.rc2023_dir} exists, skipping download")
        
        os.makedirs(self.rc2022_dir, exist_ok=True)
        if not os.path.exists(os.path.join(self.rc2022_dir, "helios2022")):
            # Download all team files from the specified URL
            download_url = "https://archive.robocup.info/Soccer/Simulation/2D/binaries/RoboCup/2022/Day4/"
            # Use wget to recursively download all files
            self.run_command(f"wget -r -np -nH --cut-dirs=7 -R 'index.html*, robots.txt' {download_url}", cwd=self.rc2022_dir)
            self.run_command(f"find {self.teams_dir} -name '*.tar.gz' -exec tar -xzvf '{{}}' -C {self.rc2022_dir} ';'", cwd=self.rc2022_dir)
            self.run_command(f"find {self.teams_dir} -name '*.tar.xz' -exec tar -xJvf '{{}}' -C {self.rc2022_dir} ';'", cwd=self.rc2022_dir)
            self.run_command(f"find {self.teams_dir} -name '*.tar.gz' -delete", cwd=self.rc2022_dir)
            self.run_command(f"find {self.teams_dir} -name '*.tar.xz' -delete", cwd=self.rc2022_dir)
        else:
            print(f"{self.rc2022_dir} exists, skipping download")

    def install_2024_teams(self):
        if not os.path.exists(os.path.join(self.rc2024_dir, "helios2024")):
            print("Downloading and extracting RoboCup 2024 teams...")

            # Google Drive から bins_day4.tar.gz をダウンロード
            file_id = "1amLM3aanMrZSxc4_ynE0ZE1oxiuDI-Bo"
            local_tar_path = os.path.join(self.base_dir, "bins_day4.tar.gz")  # 一時保存用

            gdown.download(f"https://drive.google.com/uc?id={file_id}", local_tar_path, quiet=False)

            # 解凍（この時点で bins_Day4/ が base_dir にできる）
            self.run_command(f"tar -xvf {local_tar_path} -C {self.base_dir}")

            # bins_Day4 → rc2024 にリネーム
            extracted_path = os.path.join(self.base_dir, "bins_Day4")
            
            if os.path.exists(extracted_path):
                try:
                    if not os.path.exists(self.rc2024_dir):
                        os.rename(extracted_path, self.rc2024_dir)
                    else:
                        for item in os.listdir(extracted_path):
                            s = os.path.join(extracted_path, item)
                            d = os.path.join(self.rc2024_dir, item)

                            if os.path.isdir(s):
                                if os.path.exists(d):
                                    print(f"Directory '{d}' already exists. Merging contents.")
                                shutil.copytree(s, d, dirs_exist_ok=True)
                            else:
                                print(f"Copying file '{s}' to '{d}'")
                                shutil.copy2(s, d)

                        # Copy 完了後に削除
                        shutil.rmtree(extracted_path)

                except Exception as e:
                    print(f"Error during copying or removing: {e}")
                    raise

            # 圧縮ファイルを削除
            os.remove(local_tar_path)

            # 初期設定をコピー（必要であれば）
            self.run_command(f"cp -r {self.rcsssetup_teams_dir}/. {self.teams_dir}/")
        else:
            print(f"{self.rc2024_dir} already exists. Skipping download.")


    def install_librcsc_for_helios_base(self):
        # Compile librcsc for HELIOS-Base
        os.makedirs(self.base_team_dir, exist_ok=True)
        if not os.path.exists(os.path.join(self.base_team_dir, "librcsc")):
            self.run_command("git clone -b develop https://github.com/helios-base/librcsc.git", cwd=self.base_team_dir)
            # Obtain Git LFS objects
            self.run_command("git lfs pull", cwd=os.path.join(self.base_team_dir, "librcsc"))
        else:
            print(f"{self.base_team_dir}/librcsc exists, skipping git clone")
        librcsc_dir = os.path.join(self.base_team_dir, "librcsc")
        self.run_command("git clean -xfd", cwd=librcsc_dir)
        self.run_command("./bootstrap", cwd=librcsc_dir)
        self.run_command(f"./configure --prefix={self.configure_for_teams_dir}", cwd=librcsc_dir)
        self.run_command(self.make_command, cwd=librcsc_dir)
        self.run_command("make install", cwd=librcsc_dir)

    def install_helios_base(self):
        os.makedirs(self.base_team_dir, exist_ok=True)
        # Compile librcsc for HELIOS-Base
        self.install_librcsc_for_helios_base()
        # Compile HELIOS-Base
        if not os.path.exists(os.path.join(self.base_team_dir, "helios-base")):
            self.run_command("git clone -b develop https://github.com/helios-base/helios-base.git", cwd=self.base_team_dir)
            # Obtain Git LFS objects
            self.run_command("git lfs pull", cwd=os.path.join(self.base_team_dir, "helios-base"))
        else:
            print(f"{self.base_team_dir}/helios-base exists, skipping git clone")
        helios_base_dir = os.path.join(self.base_team_dir, "helios-base")
        self.run_command("./bootstrap", cwd=helios_base_dir)
        self.run_command(f"./configure --with-librcsc={self.configure_for_teams_dir}", cwd=helios_base_dir)
        self.run_command(self.make_command, cwd=helios_base_dir)
        self.run_command("make install", cwd=helios_base_dir)

    def replace_username(self):
        # Get the username of the executor
        #username = os.getlogin()
        username = getpass.getuser()
        directory = self.user_teams_dir
        try:
            if not os.path.exists(directory):
                print(f"The specified directory does not exist: {directory}")
                return

            # Process all files in the specified directory
            for root, dirs, files in os.walk(directory):
                # Skip the .git directory
                if '.git' in dirs:
                    dirs.remove('.git')

                for file in files:
                    file_path = os.path.join(root, file)

                    # Skip binary files
                    if self.is_binary_file(file_path):
                        continue

                    # Read file content
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()

                    # Replace "/home/username/" with the executor's username
                    updated_content = content.replace('/home/username/', f'/home/{username}/')

                    # Overwrite the file with the updated content
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(updated_content)

            print("Path replacement within files has been completed")

        except Exception as e:
            # Other exceptions
            print(str(e))
            print("An unexpected error occurred")

    def is_binary_file(self, file_path):
        """
        Check if a file is binary.
        """
        try:
            with open(file_path, 'rb') as f:
                chunk = f.read(1024)
                if b'\0' in chunk:
                    return True  # Binary file
            return False  # Text file
        except Exception as e:
            # If there's an error opening the file, treat it as binary
            return True

    def add_execution_permission(self):
        # Add execution permission to scripts
        directory = self.user_teams_dir
        for root, dirs, files in os.walk(directory):
            for file in files:
                # Add execution permission based on script file extension or specific filenames
                if file.endswith('.sh') or any(substring in file for substring in ['start', 'localStartAll', 'startAll', 'startlocal']):
                    file_path = os.path.join(root, file)
                    self.run_command(f"chmod +x {file_path}")


if __name__ == "__main__":
    main()
