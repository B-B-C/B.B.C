"""
Custom exception handlers for REST Framework
"""
from rest_framework.views import exception_handler
from rest_framework import status
from rest_framework.response import Response


def custom_exception_handler(exc, context):
    """
    Custom exception handler that provides a consistent error response format.
    """
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)

    # Customize the response format
    if response is not None:
        custom_response_data = {
            'error': True,
            'status_code': response.status_code,
            'detail': response.data.get('detail', str(response.data)),
            'message': response.data.get('message', 'An error occurred'),
        }
        
        # Add field errors if they exist
        if isinstance(response.data, dict):
            field_errors = {}
            for key, value in response.data.items():
                if key not in ['detail', 'message']:
                    field_errors[key] = value
            
            if field_errors:
                custom_response_data['field_errors'] = field_errors
        
        response.data = custom_response_data

    return response


class APIError(Exception):
    """Base exception for API errors"""
    default_message = 'An error occurred'
    default_status_code = status.HTTP_400_BAD_REQUEST

    def __init__(self, message=None, status_code=None, field_errors=None):
        self.message = message or self.default_message
        self.status_code = status_code or self.default_status_code
        self.field_errors = field_errors or {}
        super().__init__(self.message)

    def to_dict(self):
        return {
            'error': True,
            'status_code': self.status_code,
            'detail': self.message,
            'message': self.message,
            'field_errors': self.field_errors,
        }



