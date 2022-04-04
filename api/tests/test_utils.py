from tests.utils import dictseq


def test_different_keys():
    d1 = {itm: itm for itm in range(10)}
    d2 = {itm: itm for itm in range(20)}
    assert not dictseq(d1, d2)


def test_different_types():
    d1 = {itm: itm for itm in range(10)}
    d2 = {itm: str(itm) for itm in range(10)}
    assert not dictseq(d1, d2)


def test_different_values():
    d1 = {itm: itm for itm in range(10)}
    d2 = {itm: itm - 1 for itm in range(10)}
    assert not dictseq(d1, d2)


def test_embedded_values():
    d1 = {"data": {itm: itm for itm in range(10)}}
    d2 = {"data": {itm: itm - 1 for itm in range(10)}}
    assert not dictseq(d1, d2)


def test_equal():
    d1 = {itm: itm for itm in range(10)}
    d2 = {itm: itm for itm in range(10)}
    assert dictseq(d1, d2)


def test_ellipsis():
    d1 = {itm: itm for itm in range(10)}
    d2 = {itm: ... for itm in range(10)}
    assert dictseq(d1, d2)
