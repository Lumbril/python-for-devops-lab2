import sys
import time
import gi
import subprocess
import click

from daemon import Daemon

gi.require_version('Notify', '0.7')

from gi.repository import Notify


class MyDaemon(Daemon):
    def __init__(self, pidfile, repo_path):
        super().__init__(pidfile)
        self.repo_path = repo_path

    def run(self):
        while True:
            subprocess.run(["git", "fetch"], cwd=self.repo_path)

            info = subprocess.run(["git", "log", "--graph",
                                   '--pretty=format:"%C(red)%h%C(reset) -%C(yellow)%d%C(reset) %s %C(green)(%cr)%C(reset)"',
                                   "--abbrev-commit", "--date=relative", "main..origin/main"],
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE,
                                  text=True,
                                  cwd=self.repo_path)

            if info.stdout:
                Notify.init("NewCommit")
                Notify.Notification.new(f"New commits found in {self.repo_path}:").show()
                Notify.Notification.new(info.stdout).show()
            elif info.returncode != 0:
                Notify.init("Error")
                Notify.Notification.new(info.stderr).show()
            else:
                Notify.init("NewCommit")
                Notify.Notification.new(f"No commits yet in {self.repo_path}").show()

            time.sleep(1)


@click.command()
@click.argument('action', type=click.Choice(['start', 'stop', 'restart']))
@click.option('--repo-path', help='Path to Git repository', type=click.Path(exists=True), required=True)
def main(action, repo_path):
    daemon = MyDaemon('/tmp/daemon_ex.pid', repo_path)

    if action == 'start':
        daemon.start()
    elif action == 'stop':
        daemon.stop()
    elif action == 'restart':
        daemon.restart()
    else:
        print("Invalid action. Use start, stop, or restart.")
        sys.exit(0)


if __name__ == '__main__':
    main()
