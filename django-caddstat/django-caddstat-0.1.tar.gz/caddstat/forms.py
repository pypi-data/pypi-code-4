"""
CADD Stat forms
"""

import re

from django import forms


def process_input(data):
    """
    Delimit the input to a list
    """

    string_input = [x for x in re.split(',|\s*', data)]
    # remove empty entries
    no_blanks = [x for x in string_input if x != '']
    number_input = [float(x) for x in no_blanks]

    return number_input


class FeedbackForm(forms.Form):
    """
    Simple form to gather feedback
    """
    name = forms.CharField()
    email = forms.EmailField()
    message = forms.CharField(widget=forms.Textarea)


class OneColumnForm(forms.Form):
    """
    Single column form
    """
    columnName = forms.CharField(required=False)
    columnData = forms.CharField(widget=forms.Textarea)

    def clean_columnData(self):
        """
        Process input data
        """
        data = self.cleaned_data['columnData']
        clean_data = process_input(data)

        return clean_data


class TwoColumnForm(forms.Form):
    """
    Two column form
    """
    columnOneName = forms.CharField(required=False)
    columnOneData = forms.CharField(widget=forms.Textarea)
    columnTwoName = forms.CharField(required=False)
    columnTwoData = forms.CharField(widget=forms.Textarea)

    def clean_columnOneData(self):
        """
        Process input data
        """
        data = self.cleaned_data['columnOneData']
        clean_data = process_input(data)

        return clean_data

    def clean_columnTwoData(self):
        """
        Process input data
        """
        data = self.cleaned_data['columnTwoData']
        clean_data = process_input(data)

        return clean_data

    def clean(self):
        """
        Check for the same number of entries in both fields
        """
        cleaned_data = super(TwoColumnForm, self).clean()
        columnOneData = cleaned_data.get('columnOneData')
        columnTwoData = cleaned_data.get('columnTwoData')
        if len(columnOneData) != len(columnTwoData):
            raise forms.ValidationError(
                'Data inputs require the same number of entries')

        return cleaned_data


class ThreeColumnForm(forms.Form):
    """
    Three column form
    """
    columnOneName = forms.CharField(required=False)
    columnOneData = forms.CharField(widget=forms.Textarea)
    columnTwoName = forms.CharField(required=False)
    columnTwoData = forms.CharField(widget=forms.Textarea)
    columnThreeName = forms.CharField(required=False)
    columnThreeData = forms.CharField(widget=forms.Textarea)

    def clean_columnOneData(self):
        """
        Process input data
        """
        data = self.cleaned_data['columnOneData']
        clean_data = process_input(data)

        return clean_data

    def clean_columnTwoData(self):
        """
        Process input data
        """
        data = self.cleaned_data['columnTwoData']
        clean_data = process_input(data)

        return clean_data

    def clean_columnThreeData(self):
        """
        Process input data
        """
        data = self.cleaned_data['columnThreeData']
        clean_data = process_input(data)

        return clean_data

    def clean(self):
        """
        Check for the same number of entries in both fields
        """
        cleaned_data = super(ThreeColumnForm, self).clean()
        columnOneData = cleaned_data.get('columnOneData')
        columnTwoData = cleaned_data.get('columnTwoData')
        columnThreeData = cleaned_data.get('columnThreeData')
        if len(columnOneData) != len(columnTwoData) | \
                len(columnOneData) != len(columnThreeData) | \
                len(columnTwoData) != len(columnThreeData):
            raise forms.ValidationError(
                'Data inputs require the same number of entries')

        return cleaned_data
