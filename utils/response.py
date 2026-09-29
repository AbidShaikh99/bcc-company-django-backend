from rest_framework.response import Response


def success_response(
    message="Success",
    data=None,
    status_code=200,
):
    return Response(
        {
            "success": True,
            "message": message,
            "data": data,
        },
        status=status_code,
    )


def error_response(
    message="Something went wrong",
    errors=None,
    status_code=400,
):
    return Response(
        {
            "success": False,
            "message": message,
            "errors": errors,
        },
        status=status_code,
    )

def delete_response(
    message="Delete Successfully",
    errors=None,
    status_code=200,
):
    return Response(
        {
            "success": True,
            "message": message,
        },
        status=status_code,
    )