from datetime import datetime

import pytest

from capture import getTime, make_request


@pytest.mark.freeze_time(datetime(2017, 3, 1, 1, 1, 1, 25000))
def test_get_time():
    time_string = getTime()
    assert time_string == '2017-03-01_01:01:01.025'


def test_make_request(mocker):
    mock_post = mocker.patch('requests.post')
    url = 'http://www.xkcd.com'
    image_bytes = b'I am an image'
    filename = 'test_file.jpg'
    files = {filename: image_bytes}

    make_request(url=url, files=files)

    mock_post.assert_called_with(url, files=files)
