from datetime import datetime

import pytest

from capture import getTime


@pytest.mark.freeze_time(datetime(2017, 3, 1, 1, 1, 1, 25000))
def test_get_time():
    time_string = getTime()
    assert time_string == '2017-03-01_01:01:01.025'
