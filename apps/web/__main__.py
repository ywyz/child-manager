import importlib

if __name__ == "__main__":
    module = importlib.import_module("apps.web.main")
    module.main()
