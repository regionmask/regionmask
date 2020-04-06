# import numpy as np
#
# from regionmask import _griddes, _dcoord
#
#
# from pytest import raises
#
#
# lat = [0.5, 1.5]
#
# def test__dcoord():
#
# assert _dcoord([0.5, 1.5]) == '1.00'
# assert _dcoord([0.5, 1.51]) == '1.01'
# assert _dcoord([0.5, 1.501]) == '1.00'
#
# assert _dcoord([0.5, 1.5, 2.5]) == '1.00'
#
# assert _dcoord([0.5, 1.5, 2.4]) == 'irr'
# assert _dcoord([0.5, 1.5, 2.501]) == 'irr'
# assert _dcoord([0.5, 1.5, 2.50001]) == '1.00'
#
#
# def test__dcoord():
# # same hash
#
# expected = ('1.00', '1.00', '3e1af5e300f0abf6f4200628b15ef5d5')
# result = _griddes([0.5, 1.5], [0.5, 1.5])
# assert result == expected
#
# result = _griddes([0.5, 1.5], [0.5, 1.5001], precision=2)
# assert result == expected
#
# result = _griddes([0.5, 1.5], [0.5, 1.5000001])
# assert result == expected
#
# # different hash
# expected = ('1.00', '1.01', '11fc981d16c9d5acbb2de30cf63a977e')
# result = _griddes([0.5, 1.5], [0.5, 1.51])
# assert result == expected
