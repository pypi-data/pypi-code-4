"""
ui.py

UC Berkeley-specific user interface.
"""
# This file is part of the schoolutils package.
# Copyright (C) 2013 Richard Lawrence <richard.lawrence@berkeley.edu>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.

from schoolutils.grading import ui
from schoolutils.institutions.ucberkeley import bspace

class UCBerkeleyUI(ui.SimpleUI):
    # Methods for Institution API:
    def csv_to_student_dicts(self, csv_path):
        return bspace.roster_csv_to_students(csv_path)
    
    def student_dicts_to_csv(self):
        pass

    def csv_to_grade_dicts(self):
        pass

    def grade_dicts_to_csv(self, file_name, grade_dicts):
        field_name_map = self.make_field_name_map()
        bspace.grades_to_gradebook_csv(file_name, grade_dicts,
                                       field_names, field_map)
        

    # Helpers:
    def make_field_name_map(self):
        """Make a dictionary mapping assignment names to
        """
        assignments = db.select_assignments(self.db_connection,
                                            course_id=self.course_id)
        fields = {}
        for a in assignments:
            
    
