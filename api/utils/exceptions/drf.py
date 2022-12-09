from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler


def core_exception_handler(exc, context):
    # If an exception is thrown that we don't explicitly handle here, we want
    # to delegate to the default exception handler offered by DRF. If we do
    # handle this exception type, we will still want access to the response
    # generated by DRF, so we get that response up front.
    response = exception_handler(exc, context)
    handlers = {
        'NotFound': _handle_not_found_error,
        'AuthenticationFailed': _handle_authentication_error,
        'NotAuthenticated': _handle_authentication_error,
        'ImproperlyConfigured': _handle_configuration_error,
        'TransitionNotAllowed': _handle_state_transition_error,
        'ValidationError': _handle_validation_error
    }
    # This is how we identify the type of the current exception. We will use
    # this in a moment to see whether we should handle this exception or let
    # Django REST Framework do it's thing.
    exception_class = exc.__class__.__name__

    if exception_class in handlers:
        # If this exception is one that we can handle, handle it. Otherwise,
        # return the response generated earlier by the default exception
        # handler.
        return handlers[exception_class](exc, context, response.exception)

    return response


def _handle_generic_error(exc, context, response):
    # This is about the most straightforward exception handler we can create.
    # We take the response generated by DRF and wrap the error message
    # from the ErrorDetail object in the `error` key.
    response.data = {
        'error': response.data.get('error')[0]
    }

    return response


def _handle_not_found_error(exc, context, response):
    view = context.get('view', None)

    if view and hasattr(view, 'queryset') and view.queryset is not None:
        error_key = view.queryset.model._meta.verbose_name

        response.data = {
            error_key: response.data.get('detail')
        }

    else:
        response = _handle_generic_error(exc, context, response)

    return response


def _handle_authentication_error(exc, context, response):
    if response.data.get('detail'):
        response.data = {
            'error': response.data['detail']
        }
    else:
        response = _handle_generic_error(exc, context, response)

    return response


def _handle_configuration_error(exc, context, response):
    response = Response({'error': str(exc)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return response


def _handle_state_transition_error(exc, context, response):
    response = Response({'error': str(exc)}, status=status.HTTP_417_EXPECTATION_FAILED)

    return response


def _handle_validation_error(exc, context, response):
    response = exception_handler(exc, context)

    if response is not None:
        if hasattr(exc.detail, 'items'):
            response.data = {}
            errors = []
            for key, value in exc.detail.items():
                errors.append('{} : {}'.format(key, ' '.join(value)))

            response.data['error'] = errors

        # serve status code in the response
        response.data['status_code'] = response.status_code

    return response