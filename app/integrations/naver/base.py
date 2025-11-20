"""
Naver Cloud Platform base client
Provides common authentication and retry logic
"""
import httpx
import uuid
from typing import Dict, Any
from tenacity import retry, stop_after_attempt, wait_exponential


class NaverBaseClient:
    """Base client for Naver Cloud Platform APIs"""
    
    def __init__(self, api_key: str, api_url: str):
        self.api_key = api_key
        self.api_url = api_url
        self.timeout = 60.0
    
    def _get_headers(self, **extra_headers) -> Dict[str, str]:
        """Get common headers for Naver API requests"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "X-NCP-CLOVASTUDIO-REQUEST-ID": str(uuid.uuid4()),
            "Content-Type": "application/json",
        }
        headers.update(extra_headers)
        return headers
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Make HTTP request with retry logic
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            **kwargs: Additional arguments for httpx request
            
        Returns:
            Response JSON data
        """
        url = f"{self.api_url}{endpoint}" if not endpoint.startswith("http") else endpoint
        
        # Merge default headers with any provided headers
        headers = self._get_headers()
        if 'headers' in kwargs:
            headers.update(kwargs['headers'])
        kwargs['headers'] = headers
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
