"""Tests a variety of python and pandas dtypes, and tests some specific
coercion examples."""

import pandas as pd
import pytest

from pandera import (
    Column, DataFrameSchema, Check, DateTime, Float, Int,
    String, Bool, Category, Object, Timedelta)
from pandera import dtypes
from pandera.errors import SchemaError


TESTABLE_DTYPES = [
    (Bool, "bool"),
    (DateTime, "datetime64[ns]"),
    (Category, "category"),
    (Float, "float64"),
    (Int, "int64"),
    (Object, "object"),
    (String, "object"),
    (Timedelta, "timedelta64[ns]"),
    ("bool", "bool"),
    ("datetime64[ns]", "datetime64[ns]"),
    ("category", "category"),
    ("float64", "float64"),
]


def test_numeric_dtypes():
    """Test every numeric type can be validated properly by schema.validate"""
    for dtype in [
            dtypes.Float,
            dtypes.Float16,
            dtypes.Float32,
            dtypes.Float64]:
        assert all(
            isinstance(
                schema.validate(
                    pd.DataFrame(
                        {"col": [-123.1, -7654.321, 1.0, 1.1, 1199.51, 5.1]},
                        dtype=dtype.value)),
                pd.DataFrame
            )
            for schema in [
                DataFrameSchema({"col": Column(dtype, nullable=False)}),
                DataFrameSchema({"col": Column(dtype.value, nullable=False)})
            ]
        )

    for dtype in [
            dtypes.Int,
            dtypes.Int8,
            dtypes.Int16,
            dtypes.Int32,
            dtypes.Int64]:
        assert all(
            isinstance(
                schema.validate(
                    pd.DataFrame(
                        {"col": [-712, -4, -321, 0, 1, 777, 5, 123, 9000]},
                        dtype=dtype.value)),
                pd.DataFrame
            )
            for schema in [
                DataFrameSchema({"col": Column(dtype, nullable=False)}),
                DataFrameSchema({"col": Column(dtype.value, nullable=False)})
            ]
        )

    for dtype in [
            dtypes.UInt8,
            dtypes.UInt16,
            dtypes.UInt32,
            dtypes.UInt64]:
        assert all(
            isinstance(
                schema.validate(
                    pd.DataFrame(
                        {"col": [1, 777, 5, 123, 9000]},
                        dtype=dtype.value)),
                pd.DataFrame
            )
            for schema in [
                DataFrameSchema({"col": Column(dtype, nullable=False)}),
                DataFrameSchema({"col": Column(dtype.value, nullable=False)})
            ]
        )


def test_category_dtype():
    """Test the category type can be validated properly by schema.validate"""
    schema = DataFrameSchema(
        columns={
            "col": Column(
                dtypes.Category,
                checks=[
                    Check(lambda s: set(s) == {"A", "B", "C"}),
                    Check(lambda s:
                          s.cat.categories.tolist() == ["A", "B", "C"]),
                    Check(lambda s: s.isin(["A", "B", "C"]))
                ],
                nullable=False
            ),
        },
        coerce=False
    )
    validated_df = schema.validate(
        pd.DataFrame(
            {"col": pd.Series(["A", "B", "A", "B", "C"], dtype="category")}
        )
    )
    assert isinstance(validated_df, pd.DataFrame)


def test_category_dtype_coerce():
    """Test coercion of the category type is validated properly by
    schema.validate and fails safely."""
    columns = {
        "col": Column(
            dtypes.Category,
            checks=Check(lambda s: set(s) == {"A", "B", "C"}),
            nullable=False
        ),
    }

    with pytest.raises(SchemaError):
        DataFrameSchema(columns=columns, coerce=False).validate(
            pd.DataFrame(
                {"col": pd.Series(["A", "B", "A", "B", "C"], dtype="object")}
            )
        )

    validated_df = DataFrameSchema(columns=columns, coerce=True).validate(
        pd.DataFrame(
            {"col": pd.Series(["A", "B", "A", "B", "C"], dtype="object")}
        )
    )
    assert isinstance(validated_df, pd.DataFrame)


def test_datetime():
    """Test datetime types can be validated properly by schema.validate"""
    schema = DataFrameSchema(
        columns={
            "col": Column(
                dtypes.DateTime,
                checks=Check(lambda s: s.min() > pd.Timestamp("2015")),
            )
        }
    )

    validated_df = schema.validate(
        pd.DataFrame(
            {"col": pd.to_datetime(["2019/01/01", "2018/05/21", "2016/03/10"])}
        )
    )

    assert isinstance(validated_df, pd.DataFrame)

    with pytest.raises(SchemaError):
        schema.validate(
            pd.DataFrame(
                {"col": pd.to_datetime(["2010/01/01"])}
            )
        )
