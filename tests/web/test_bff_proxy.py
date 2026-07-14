import pytest


@pytest.mark.asyncio
async def test_fetch_api_structure():
    """BFF 客户端应该有正确的结构"""
    from apps.web import main
    
    assert hasattr(main, 'api_client')
    assert hasattr(main, 'fetch_api')


def test_api_client_configuration():
    """BFF 客户端应该配置正确的 API 基础 URL"""
    from apps.web import main
    
    assert main.api_client.base_url.host == "127.0.0.1"
    assert str(main.api_client.base_url.port) == "28000"