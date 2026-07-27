"""首期 AI 客户端的固定安全限制。"""

import httpx

AI_TIMEOUT = httpx.Timeout(connect=5.0, read=60.0, write=10.0, pool=5.0)
MAX_RESPONSE_BYTES = 2 * 1024 * 1024
