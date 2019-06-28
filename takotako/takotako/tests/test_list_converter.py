# coding: utf-8
from django.test import TestCase
from parameterized import parameterized
from takotako.nornir2.tasks_parser.list_converter import (
    convertsSameModule,
    returnsInterfaceCmdList,
    sortsModuleInterfaces,
    optimizesWithRange,
)


class Test_ListConverter(TestCase):
    @parameterized.expand(
        [
            [
                ["gi1/0/2", "gi2/0/3", "gi1/0/3", "gi1/0/1", "gi3/0/5", "gi3/0/6"],
                ["range gi1/0/1 - 3", "gi2/0/3", "range gi3/0/5 - 6"],
            ]
        ]
    )
    def test_optimizesWithRange(self, inputList, expected):
        result = optimizesWithRange(inputList)
        assert result == expected

    @parameterized.expand(
        [
            [
                ["gi1/0/1", "gi1/0/3", "gi2/0/3", "gi3/0/5"],
                {1: ["gi1/0/1", "gi1/0/3"], 2: ["gi2/0/3"], 3: ["gi3/0/5"]},
            ]
        ]
    )
    def test_sortsModuleInterfaces(self, inputList, expected):
        result = sortsModuleInterfaces(inputList)
        assert result == expected

    @parameterized.expand(
        [
            [["gi1/0/1"], ([[1]], "gi1")],
            [["gi1/0/3", "gi1/0/4", "gi1/0/5", "gi1/0/6"], ([[3, 6]], "gi1")],
            [
                [
                    "gi1/0/1",
                    "gi1/0/3",
                    "gi1/0/4",
                    "gi1/0/5",
                    "gi1/0/6",
                    "gi1/0/7",
                    "gi1/0/8",
                    "gi1/0/9",
                ],
                ([[1], [3, 9]], "gi1"),
            ],
            [
                [
                    "gi1/0/1",
                    "gi1/0/3",
                    "gi1/0/4",
                    "gi1/0/5",
                    "gi1/0/6",
                    "gi1/0/7",
                    "gi1/0/8",
                    "gi1/0/9",
                    "gi1/0/11",
                ],
                ([[1], [3, 9], [11]], "gi1"),
            ],
            [
                [
                    "gi1/0/1",
                    "gi1/0/2",
                    "gi1/0/5",
                    "gi1/0/7",
                    "gi1/0/8",
                    "gi1/0/9",
                    "gi1/0/11",
                ],
                ([[1, 2], [5], [7, 9], [11]], "gi1"),
            ],
            [
                [
                    "gi1/0/1",
                    "gi1/0/3",
                    "gi1/0/4",
                    "gi1/0/5",
                    "gi1/0/7",
                    "gi1/0/8",
                    "gi1/0/9",
                    "gi1/0/11",
                    "gi1/0/13",
                    "gi1/0/14",
                    "gi1/0/18",
                    "gi1/0/19",
                ],
                ([[1], [3, 5], [7, 9], [11], [13, 14], [18, 19]], "gi1"),
            ],
        ]
    )
    def test_convertsSameModule(self, inputList, expected):
        """
        Same module, returns range whenever possible
        """
        result = convertsSameModule(inputList)
        assert result == expected

    @parameterized.expand(
        [
            [[[1]], "gi1", ["gi1/0/1"]],
            [[[3, 6]], "gi1", ["range gi1/0/3 - 6"]],
            [[[1], [3, 6]], "gi1", ["gi1/0/1", "range gi1/0/3 - 6"]],
        ]
    )
    def test_returnsInterfaceCmdList(self, resultList, prefixe, expected):
        result = returnsInterfaceCmdList(resultList, prefixe)
        assert result == expected
