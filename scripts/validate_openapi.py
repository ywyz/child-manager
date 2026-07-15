import sys
from pathlib import Path

from openapi_spec_validator import validate_spec


def main() -> None:
    spec_path = (
        Path(__file__).resolve().parents[1] / "specs/001-daily-activity-plan/contracts/openapi.yaml"
    )
    if not spec_path.exists():
        print(f"OpenAPI spec not found: {spec_path}")
        sys.exit(1)

    import yaml

    with spec_path.open() as f:
        spec = yaml.safe_load(f)

    validate_spec(spec)
    print("OpenAPI spec is valid")


if __name__ == "__main__":
    main()
