import os

from alembic.config import Config


def test_alembic_config_exists():
    """Alembic 配置文件应该存在"""
    config_path = os.path.join(
        os.path.dirname(__file__),
        "..",
        "..",
        "alembic.ini",
    )
    assert os.path.exists(config_path), "alembic.ini 应该存在"


def test_alembic_script_directory_exists():
    """Alembic 脚本目录应该存在"""
    script_path = os.path.join(
        os.path.dirname(__file__),
        "..",
        "..",
        "packages",
        "backend",
        "database",
        "migrations",
    )
    assert os.path.exists(script_path), "migrations 目录应该存在"


def test_alembic_config_is_valid():
    """Alembic 配置应该有效"""
    config = Config("alembic.ini")
    
    assert config.get_main_option("script_location") is not None


def test_alembic_has_env_py():
    """Alembic 应该有 env.py"""
    env_path = os.path.join(
        os.path.dirname(__file__),
        "..",
        "..",
        "packages",
        "backend",
        "database",
        "migrations",
        "env.py",
    )
    assert os.path.exists(env_path), "env.py 应该存在"