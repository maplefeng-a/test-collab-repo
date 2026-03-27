"""
Bob's API Module
================

Utility functions and classes for API operations.
This module provides helper functions for making HTTP requests,
handling responses, and common API patterns.

Author: bob
Date: 2026-03-29
"""

import json
from typing import Any, Dict, Optional, Union
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError


class APIError(Exception):
    """Custom exception for API-related errors."""
    
    def __init__(self, message: str, status_code: Optional[int] = None):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class APIClient:
    """
    A simple HTTP API client for making REST API calls.
    
    Attributes:
        base_url (str): The base URL for all API requests
        headers (Dict): Default headers to include in all requests
        timeout (int): Request timeout in seconds
    """
    
    def __init__(self, base_url: str, headers: Optional[Dict[str, str]] = None, timeout: int = 30):
        """
        Initialize the API client.
        
        Args:
            base_url: The base URL for the API (e.g., 'https://api.example.com')
            headers: Optional dictionary of default headers
            timeout: Request timeout in seconds (default: 30)
        """
        self.base_url = base_url.rstrip('/')
        self.headers = headers or {}
        self.timeout = timeout
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Make an HTTP request to the API.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE, etc.)
            endpoint: API endpoint (e.g., '/users')
            data: Optional dictionary of data to send in request body
            headers: Optional additional headers for this request
            
        Returns:
            Dictionary containing the JSON response
            
        Raises:
            APIError: If the request fails or returns an error status
        """
        url = f"{self.base_url}{endpoint}"
        request_headers = {**self.headers, **(headers or {})}
        
        if data is not None:
            request_headers['Content-Type'] = 'application/json'
            body = json.dumps(data).encode('utf-8')
        else:
            body = None
        
        request = Request(url, data=body, headers=request_headers, method=method)
        
        try:
            with urlopen(request, timeout=self.timeout) as response:
                response_data = response.read().decode('utf-8')
                return json.loads(response_data) if response_data else {}
        except HTTPError as e:
            raise APIError(f"HTTP Error {e.code}: {e.reason}", status_code=e.code)
        except URLError as e:
            raise APIError(f"URL Error: {e.reason}")
        except json.JSONDecodeError as e:
            raise APIError(f"JSON Decode Error: {str(e)}")
    
    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Make a GET request.
        
        Args:
            endpoint: API endpoint
            params: Optional query parameters
            
        Returns:
            Response data as dictionary
        """
        if params:
            query_string = '&'.join(f"{k}={v}" for k, v in params.items())
            endpoint = f"{endpoint}?{query_string}"
        return self._make_request('GET', endpoint)
    
    def post(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make a POST request.
        
        Args:
            endpoint: API endpoint
            data: Data to send in request body
            
        Returns:
            Response data as dictionary
        """
        return self._make_request('POST', endpoint, data=data)
    
    def put(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make a PUT request.
        
        Args:
            endpoint: API endpoint
            data: Data to send in request body
            
        Returns:
            Response data as dictionary
        """
        return self._make_request('PUT', endpoint, data=data)
    
    def delete(self, endpoint: str) -> Dict[str, Any]:
        """
        Make a DELETE request.
        
        Args:
            endpoint: API endpoint
            
        Returns:
            Response data as dictionary
        """
        return self._make_request('DELETE', endpoint)


def create_api_client(base_url: str, api_key: Optional[str] = None) -> APIClient:
    """
    Factory function to create an API client with optional authentication.
    
    Args:
        base_url: The base URL for the API
        api_key: Optional API key for authentication
        
    Returns:
        Configured APIClient instance
    """
    headers = {}
    if api_key:
        headers['Authorization'] = f'Bearer {api_key}'
    
    return APIClient(base_url, headers=headers)


def validate_response(response: Dict[str, Any], required_fields: list) -> bool:
    """
    Validate that a response contains all required fields.
    
    Args:
        response: The API response dictionary
        required_fields: List of field names that must be present
        
    Returns:
        True if all required fields are present, False otherwise
    """
    return all(field in response for field in required_fields)


def format_error_message(error: Exception, context: str = "") -> str:
    """
    Format an error message with optional context.
    
    Args:
        error: The exception object
        context: Optional context about where the error occurred
        
    Returns:
        Formatted error message string
    """
    if context:
        return f"[{context}] {type(error).__name__}: {str(error)}"
    return f"{type(error).__name__}: {str(error)}"


# Example usage
if __name__ == "__main__":
    # Example: Create a client and make requests
    client = create_api_client("https://api.example.com", api_key="your-api-key")
    
    try:
        # GET request
        users = client.get("/users", params={"limit": 10})
        print(f"Users: {users}")
        
        # POST request
        new_user = client.post("/users", data={"name": "John", "email": "john@example.com"})
        print(f"Created user: {new_user}")
        
    except APIError as e:
        print(format_error_message(e, "API Call"))
