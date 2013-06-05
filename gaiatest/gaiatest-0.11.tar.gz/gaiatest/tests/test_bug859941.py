from gaiatest import GaiaTestCase


class TestDismissKeyboard(GaiaTestCase):

    def test_dismiss_keyboard(self):
        self.apps.launch('Contacts')
        self.marionette.tap(self.marionette.find_element('id', 'add-contact-button'))
        self.wait_for_element_displayed('id', 'save-button')
        self.marionette.find_element('id', 'givenName').clear()
        self.marionette.find_element('id', 'givenName').send_keys('D')
        self.marionette.find_element('id', 'save-button').tap()
        self.marionette.switch_to_frame()
        self.marionette.switch_to_frame(self.marionette.find_element('css selector', '#keyboard-frame iframe'), focus=False)
        import time
        time.sleep(5)
        self.assertEqual(self.marionette.find_element('id', 'keyboard').get_attribute('data-hidden'), 'true')
