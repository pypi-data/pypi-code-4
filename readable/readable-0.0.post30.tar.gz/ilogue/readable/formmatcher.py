import webtest
from ilogue.readable.matcher import Matcher


class FormMatcher():

    def __init__(self, forms, testappBased=True):
        self.forms = list(forms.values())
        self.isTestappBased = testappBased
        self.fullformstext = '\n'
        for form in self.forms:
            self.fullformstext += '\n' + form.text

    def assertMatch(self, crit, val):
        MSG = ("No matching form found with {0}" +
            " with expected value: '{1}'. All forms: ")
        if len(self.forms) == 0:
            raise AssertionError(MSG.format(crit,
                str(val)) + self.fullformstext)

    def withAction(self, expectedUrl):
        for form in self.forms:
            if not form.action == expectedUrl:
                self.forms.remove(form)
        self.assertMatch('action', expectedUrl)
        return self

    def withMethod(self, method):
        for form in self.forms:
            if not form.method == method:
                self.forms.remove(form)
        self.assertMatch('method', method)
        return self

    def withTextFieldWithName(self, expectedName):
        for form in self.forms:
            if not expectedName in form.fields:
                self.forms.remove(form)
            elif not isinstance(form[expectedName], webtest.Text):
                self.forms.remove(form)
        self.assertMatch('text field with name', expectedName)
        return self

    def withSubmitButtonLabeled(self, label):
        for form in self.forms:
            for f in form.fields.items():
                fieldObject = f[1][0]
                if isinstance(fieldObject, webtest.Submit):
                    if self.fieldHasValue(fieldObject, label):
                        break
            else:
                self.forms.remove(form)
        self.assertMatch('submit button with label', label)
        return self

    def withHiddenFieldWithValue(self, name, value):
        for form in self.forms:
            if not name in form.fields:
                self.forms.remove(form)
            elif not isinstance(form[name],  webtest.Hidden):
                self.forms.remove(form)
            elif not self.fieldHasValue(form[name], value):
                self.forms.remove(form)
        self.assertMatch('hidden field with name and value',
            name + ', ' + value)
        return self

    def fieldHasValue(self, objectOuter, expectedValue):
        innerObject = objectOuter
        #workaround, WebTest.Field does not expose value:
        actualValue = innerObject._value
        if isinstance(expectedValue, Matcher):
            return expectedValue.matches(actualValue)
        else:
            return actualValue == expectedValue

    #not part of this objects responsibilities, should go somewhere else. (on the TestCae?)
    def submit(self, toServerApp=None):
        MSGMULTIPLE = "Multiple forms match, cannot submit."
        MSGNOTSUPP = ("Must either be a WebTest.TestApp based form" +
            " or provide toServerApp argument to use submit().")
        if len(self.forms) > 1:
            raise AssertionError(MSGMULTIPLE + self.fullformstext)
        if not (self.isTestappBased or toServerApp):
            raise TypeError(MSGNOTSUPP)
        if toServerApp:
            toServerApp.post(self.forms[0].action,dict(self.forms[0].submit_fields()))
        else:
            self.forms[0].submit()
