import pytest
import math
from vector2 import Vector2


class TestVector2Init:
    def test_init_default(self):
        v = Vector2()
        assert v.x == 0
        assert v.y == 0

    def test_init_with_values(self):
        v = Vector2(3, 4)
        assert v.x == 3
        assert v.y == 4

    def test_init_converts_to_float(self):
        v = Vector2(3, 4)
        assert isinstance(v.x, float)
        assert isinstance(v.y, float)


class TestVector2Operations:
    def test_add(self):
        v1 = Vector2(1, 2)
        v2 = Vector2(3, 4)
        result = v1 + v2
        assert result.x == 4
        assert result.y == 6

    def test_mul_scalar(self):
        v = Vector2(2, 3)
        result = v * 2
        assert result.x == 4
        assert result.y == 6

    def test_rmul_scalar(self):
        v = Vector2(2, 3)
        result = 2 * v
        assert result.x == 4
        assert result.y == 6

    def test_mul_zero(self):
        v = Vector2(5, 10)
        result = v * 0
        assert result.x == 0
        assert result.y == 0

    def test_mul_negative(self):
        v = Vector2(2, 3)
        result = v * -1
        assert result.x == -2
        assert result.y == -3


class TestVector2Length:
    def test_length_zero(self):
        v = Vector2(0, 0)
        assert v.length() == 0

    def test_length_3_4_5(self):
        v = Vector2(3, 4)
        assert v.length() == 5

    def test_length_unit(self):
        v = Vector2(1, 0)
        assert v.length() == 1


class TestVector2Distance:
    def test_distance_same_point(self):
        v1 = Vector2(0, 0)
        v2 = Vector2(0, 0)
        assert v1.distance_to(v2) == 0

    def test_distance_3_4_5(self):
        v1 = Vector2(0, 0)
        v2 = Vector2(3, 4)
        assert v1.distance_to(v2) == 5

    def test_distance_symmetric(self):
        v1 = Vector2(1, 2)
        v2 = Vector2(4, 6)
        assert v1.distance_to(v2) == v2.distance_to(v1)


class TestVector2Normalize:
    def test_normalize_zero(self):
        v = Vector2(0, 0)
        result = v.normalize()
        assert result.x == 0
        assert result.y == 0

    def test_normalize_unit(self):
        v = Vector2(3, 4)
        result = v.normalize()
        assert abs(result.length() - 1.0) < 1e-6

    def test_normalize_preserves_direction(self):
        v = Vector2(3, 4)
        result = v.normalize()
        assert abs(result.x - 0.6) < 1e-6
        assert abs(result.y - 0.8) < 1e-6


class TestVector2Equality:
    def test_equal_vectors(self):
        v1 = Vector2(1, 2)
        v2 = Vector2(1, 2)
        assert v1 == v2

    def test_not_equal_vectors(self):
        v1 = Vector2(1, 2)
        v2 = Vector2(2, 3)
        assert not (v1 == v2)

    def test_equal_with_float_precision(self):
        v1 = Vector2(1.0, 2.0)
        v2 = Vector2(1.0 + 1e-7, 2.0 + 1e-7)
        assert v1 == v2


class TestVector2Repr:
    def test_repr(self):
        v = Vector2(1.5, 2.5)
        assert "Vector2" in repr(v)
        assert "1.5" in repr(v)
        assert "2.5" in repr(v)
