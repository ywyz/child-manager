"""CLI 入口。"""

from packages.backend.bootstrap.init_admin import run_init_admin

if __name__ == "__main__":
    print(run_init_admin())
