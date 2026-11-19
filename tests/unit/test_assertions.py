import pytest

from apiwatch.models import APIResult


def create_result(**kwargs):

    defaults = {
        "url": "https://example.com/api",
        "method": "GET",
        "status_code": 200,
        "response_time": 0.5,
        "is_success": True,
        "response_size": 100,
    }

    defaults.update(kwargs)

    return APIResult(**defaults)


def test_assert_status_code_passes():

    result = create_result(status_code=200)

    result.assert_status_code(200)


def test_assert_status_code_fails():

    result = create_result(status_code=404)

    with pytest.raises(AssertionError):

        result.assert_status_code(200)


def test_assert_success_passes():

    result = create_result(is_success=True)

    result.assert_success()


def test_assert_success_fails():

    result = create_result(
        is_success=False,
        status_code=500,
        error="Internal Server Error",
    )

    with pytest.raises(AssertionError):

        result.assert_success()


def test_assert_response_time_passes():

    result = create_result(response_time=0.5)

    result.assert_response_time(1.0)


def test_assert_response_time_fails():

    result = create_result(response_time=3.0)

    with pytest.raises(AssertionError):

        result.assert_response_time(1.0)


def test_assert_valid_passes():

    result = create_result(
        is_valid=True,
        validation_errors=[],
    )

    result.assert_valid()


def test_assert_valid_fails():

    result = create_result(
        is_valid=False,
        validation_errors=["id: expected integer"],
    )

    with pytest.raises(AssertionError):

        result.assert_valid()


def test_assert_no_errors_passes():

    result = create_result(
        is_success=True,
        is_valid=True,
        validation_errors=[],
    )

    result.assert_no_errors()


def test_assert_no_errors_fails_with_request_error():

    result = create_result(
        is_success=False,
        error="Connection timeout",
    )

    with pytest.raises(AssertionError):

        result.assert_no_errors()


def test_assert_no_errors_fails_with_validation_errors():

    result = create_result(
        is_success=True,
        is_valid=False,
        validation_errors=["id: expected integer"],
    )

    with pytest.raises(AssertionError):

        result.assert_no_errors()