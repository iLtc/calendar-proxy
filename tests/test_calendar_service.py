from unittest.mock import patch, Mock

import calendar_service

MINIMAL_ICS = "BEGIN:VCALENDAR\r\nVERSION:2.0\r\nPRODID:-//test//EN\r\nEND:VCALENDAR\r\n"


def test_fetch_calendar_uses_10_second_timeout():
    mock_response = Mock()
    mock_response.text = MINIMAL_ICS
    mock_response.raise_for_status = Mock()

    with patch("calendar_service.requests.get", return_value=mock_response) as mock_get:
        calendar_service.fetch_calendar("https://example.com/cal.ics")

    mock_get.assert_called_once_with("https://example.com/cal.ics", timeout=10)
