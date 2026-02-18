import time

def request_timing_middleware(get_response):
    """
    Function-based middleware to log request processing time
    """

    def middleware(request):
        start_time = time.time()

        response = get_response(request)

        duration = time.time() - start_time
        print(f"{request.path} took {duration:.2f} seconds. Completed with status {response.status_code}.")

        return response

    return middleware