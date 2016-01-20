def remove_headers_from_response(response, *headers):
    """Removes the given headers from the response using the clean_headers middleware."""
    response.clean_headers = headers