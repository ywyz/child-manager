import importlib

if __name__ == "__main__":
    module = importlib.import_module("apps.worker.main")
    module.main()
