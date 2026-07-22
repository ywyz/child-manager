"""WebAuthn 浏览器 options 的公共 seam。"""

from collections.abc import Sequence


def registration_options(
    *,
    challenge: str,
    rp_id: str,
    rp_name: str,
    user_handle: bytes,
    username: str,
    display_name: str,
    exclude_credential_ids: Sequence[bytes] = (),
) -> dict[str, object]:
    """T029 将生成可直接传给 navigator.credentials.create 的 JSON。"""

    del (
        challenge,
        rp_id,
        rp_name,
        user_handle,
        username,
        display_name,
        exclude_credential_ids,
    )
    return {}


def authentication_options(
    *,
    challenge: str,
    rp_id: str,
    allow_credential_ids: Sequence[bytes] = (),
) -> dict[str, object]:
    """T029 将生成可直接传给 navigator.credentials.get 的 JSON。"""

    del challenge, rp_id, allow_credential_ids
    return {}
