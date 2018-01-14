# test_common.py

from __future__ import unicode_literals

import pytest

import itertools

from csv23._common import is_8bit_clean, _open_csv


def test_is_8bit_clean():
    assert is_8bit_clean('u8')
    assert not is_8bit_clean('u16')
    assert is_8bit_clean('windows-1252')
    assert not is_8bit_clean('utf-16')
    assert is_8bit_clean('IBM437')
    assert not is_8bit_clean('cp500')
    assert not is_8bit_clean('UTF-16BE')


@pytest.mark.parametrize('event', ['close', 'gc', RuntimeError])
def test_open_csv(mocker, mock_open, event):
    stream = mock_open.return_value
    csv_func = mocker.Mock(return_value=itertools.count())
    filename, dialect = mocker.sentinel.filename, mocker.sentinel.dialect

    def iterrows():
        with _open_csv(filename, {}, csv_func, dialect, {}) as reader:
            for row in reader:
                yield row

    r = iterrows()
    assert next(r) == 0
    mock_open.assert_called_once_with(filename)
    csv_func.assert_called_once_with(stream, dialect=dialect)
    assert not stream.close.called

    assert next(r) == 1
    mock_open.assert_called_once()
    assert not stream.close.called

    if event == 'close':
        r.close()
    elif event == 'gc':
        del r
    else:
        with pytest.raises(event):
            raise event
    mock_open.assert_called_once()
    assert stream.close.called_once_with()
