from fastapi import Request
from starlette.responses import JSONResponse


class AppExceptionCase(Exception):
    def __init__(self, status_code: int, context: dict):
        self.exception_case = self.__class__.__name__
        self.status_code = status_code
        self.context = context

    def __str__(self):
        return (
            f"<AppException {self.exception_case} - "
            + f"status_code={self.status_code} - context={self.context}>"
        )


async def app_exception_handler(request: Request, exc: AppExceptionCase):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "app_exception": exc.exception_case,
            "context": exc.context,
        },
    )


class AppException(object):
    class AddItem(AppExceptionCase):
        def __init__(self, context: dict = None):
            """
            Item creation failed
            """
            status_code = 400
            AppExceptionCase.__init__(self, status_code, context)

    class InvalidItem(AppExceptionCase):
        def __init__(self, context: dict = None):
            """
            Item is invalid
            """
            status_code = 400
            AppExceptionCase.__init__(self, status_code, context)

    class GetItem(AppExceptionCase):
        def __init__(self, context: dict = None):
            """
            Item not found
            """
            status_code = 404
            AppExceptionCase.__init__(self, status_code, context)

    class RequiresAuth(AppExceptionCase):
        def __init__(self, context: dict = None):
            """
            Item is not public and requires auth
            """
            status_code = 401
            AppExceptionCase.__init__(self, status_code, context)

    class DeleteItem(AppExceptionCase):
        def __init__(self, context: dict = None):
            """
            No credit requests with that email
            """
            status_code = 403
            AppExceptionCase.__init__(self, status_code, context)

    class InvalidAccount(AppExceptionCase):
        def __init__(self, context: dict = None):
            """
            Invalid username or password
            """
            status_code = 403
            AppExceptionCase.__init__(self, status_code, context)