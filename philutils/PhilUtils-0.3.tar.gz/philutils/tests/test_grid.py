#!/usr/bin/env python

#Name: test_grid.py
#Author: Philip Zerull
#Date Created: Friday August 9, 2013


import os
import sys
import unittest
from philutils.containers import Grid


class GridTest(unittest.TestCase):
    def test_grid_creation_one_dim_array(self):
        grid = Grid(5)
        self.assertEqual(grid._data, [None]*5)

    def test_that_creating_a_grid_without_any_size_raises_error(self):
        try:
            Grid()
        except ValueError as err:
            expected_msg = 'Must have at least one dimension'
            self.assertEqual(err.message, expected_msg)

    def test_invalid_number_of_parameters_with_grid_with_multi_dims(self):
        grid = Grid(3, 4, 5)
        try:
            value = grid[2, 3]
        except ValueError as err:
            expected = 'incorrect number of indexes provided'
            self.assertEqual(err.message, expected)

    def test_invalid_number_of_parameters_with_grid_with_single_dim(self):
        grid = Grid(3, 4, 5)
        try:
            value = grid[3]
        except ValueError as err:
            expected = 'incorrect number of indexes provided'
            self.assertEqual(err.message, expected)

    def test_invalid_number_of_parameters_when_setting_with_multi_dims(self):
        grid = Grid(3, 4, 5)
        try:
            grid[2, 3] = 'banana'
        except ValueError as err:
            expected = 'incorrect number of indexes provided'
            self.assertEqual(err.message, expected)

    def test_invalid_number_of_parameters_when_setting_with_single_dim(self):
        grid = Grid(3, 4, 5)
        try:
            grid[3] = 'banana'
        except ValueError as err:
            expected = 'incorrect number of indexes provided'
            self.assertEqual(err.message, expected)

    def test_grid_creation_n_dimenstional_array(self):
        grid = Grid(2, 3, 4)
        self.assertEqual(grid._data, [[[None]*4]*3]*2)

    def test_setting_of_item(self):
        grid = Grid(2, 2, 3, 4)
        grid[0, 1, 0, 1] = 'banana'
        self.assertEqual(grid._data[0][1][0][1], 'banana')

    def test_getting_of_item(self):
        grid = Grid(2, 2, 3, 4, 4)
        grid._data[0][1][0][1][3] = 'monkey'
        self.assertEqual(grid[0, 1, 0, 1, 3], 'monkey')

    def test_setting_of_item_and_getting_of_item_get_to_same_location(self):
        grid = Grid(2, 2, 3, 4)
        grid[1, 1, 1, 1] = 'banana'
        self.assertEqual(grid[[1, 1, 1, 1]], 'banana')

    def test_deleting_sets_item_to_none(self):
        grid = Grid(4)
        grid._data[2] = 'banana'
        del grid[2]
        self.assertEqual(grid[2], None)
