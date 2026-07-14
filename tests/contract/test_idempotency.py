"""幂等请求摘要必须覆盖实际资源与语义输入。"""

from packages.contracts.common import canonical_request_fingerprint


def fingerprint(
    *, path_params: dict[str, object], query: list[tuple[str, str]], body: object
) -> str:
    return canonical_request_fingerprint(
        method="POST",
        route_template="/api/v1/plans/{plan_id}/ai/generations",
        path_params=path_params,
        query_params=query,
        body=body,
    )


def test_fingerprint_changes_across_actual_path_resources() -> None:
    first = fingerprint(path_params={"plan_id": "PLAN-A"}, query=[], body={"section": "morning"})
    second = fingerprint(path_params={"plan_id": "PLAN-B"}, query=[], body={"section": "morning"})

    assert first != second


def test_fingerprint_is_stable_for_equivalent_query_and_json_order() -> None:
    first = fingerprint(
        path_params={"plan_id": "01900000-0000-7000-8000-000000000001"},
        query=[("profile", "b"), ("profile", "a")],
        body={"expected_version": 3, "section": "morning"},
    )
    second = fingerprint(
        path_params={"plan_id": "01900000-0000-7000-8000-000000000001"},
        query=[("profile", "a"), ("profile", "b")],
        body={"section": "morning", "expected_version": 3},
    )

    assert first == second
    assert len(first) == 64
