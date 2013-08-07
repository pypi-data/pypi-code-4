# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from marionette.by import By
from marionette.marionette import Actions
from marionette.keys import Keys

from gaiatest.apps.base import Base
from gaiatest.apps.base import PageRegion


class EverythingMe(Base):

    # Homescreen locators
    _homescreen_frame_locator = (By.CSS_SELECTOR, 'div.homescreen > iframe')

    # Everything.Me locators
    _search_box_locator = (By.ID, 'search-q')
    _search_title_locator = (By.ID, 'search-title')
    _loading_apps_locator = (By.CSS_SELECTOR, 'div.loading-apps')
    _category_item_locator = (By.CSS_SELECTOR, '#shortcuts-items li[data-query]')
    _app_icon_locator = (By.CSS_SELECTOR, 'li.cloud[data-name]')

    def go_to_everything_me(self):
        # Move this into the homescreen app when it is created
        hs_frame = self.marionette.find_element(*self._homescreen_frame_locator)
        self.marionette.switch_to_frame(hs_frame)

        self.marionette.execute_script('window.wrappedJSObject.GridManager.goToPreviousPage();')
        self.wait_for_condition(lambda m: m.find_element('tag name', 'body')
            .get_attribute('data-transitioning') != 'true')

    def wait_for_search_box_displayed(self):
        self.wait_for_element_displayed(*self._search_box_locator)

    def type_into_search_box(self, text_to_type):
        search_input = self.marionette.find_element(*self._search_box_locator)
        search_input.clear()
        search_input.send_keys(text_to_type)
        search_input.send_keys(Keys.RETURN)

    @property
    def search_title(self):
        self.wait_for_element_displayed(*self._search_title_locator)
        return self.marionette.find_element(*self._search_title_locator).text

    def wait_for_categories_to_load(self):
        self.wait_for_element_not_displayed(*self._loading_apps_locator)
        self.wait_for_element_displayed(*self._category_item_locator)

    def tap_category(self, category_name):
        for category in self.categories:
            if category.name.lower() == category_name.lower():
                category.tap()
                break
        else:
            raise Exception('Category with "%s" name is not present' % category_name)

    @property
    def categories_count(self):
        return len(self.marionette.find_elements(*self._category_item_locator))

    @property
    def categories(self):
        return [EverythingMeCategory(self.marionette, root_el) for root_el in
                self.marionette.find_elements(*self._category_item_locator)]

    def wait_for_app_icons_displayed(self):
        self.wait_for_element_displayed(*self._app_icon_locator)

    @property
    def apps_count(self):
        return len(self.marionette.find_elements(*self._app_icon_locator))

    @property
    def app_icons(self):
        return [EverythingMeApp(self.marionette, root_el) for root_el in
                self.marionette.find_elements(*self._app_icon_locator)]

    def tap_app_icon(self, app_name):
        for app in self.app_icons:
            if app.name.lower() == app_name.lower():
                app.tap()
                break
        else:
            raise Exception('App with "%s" name is not present' % app_name)


class EverythingMeCategory(PageRegion):

    @property
    def name(self):
        return self.root_element.get_attribute('data-query')

    def tap(self):
        self.root_element.tap()


class EverythingMeApp(PageRegion):

    _app_iframe_locator = (By.CSS_SELECTOR, 'iframe[data-origin-name="%s"]')

    # Modal dialog locators
    _modal_dialog_message_locator = (By.ID, 'modal-dialog-confirm-message')
    _modal_dialog_ok_locator = (By.ID, 'modal-dialog-confirm-ok')

    @property
    def name(self):
        return self.root_element.get_attribute('data-name')

    def tap(self):
        _app_iframe_locator = (self._app_iframe_locator[0],
                               self._app_iframe_locator[1] % self.name)

        self.root_element.tap()
        # Switch to top level frame then look for the app
        # Find the frame and switch to it
        self.marionette.switch_to_frame()
        app_iframe = self.wait_for_element_present(*_app_iframe_locator)
        self.marionette.switch_to_frame(app_iframe)

        # wait for app to launch
        self.wait_for_condition(lambda m: m.title)

    def tap_to_install(self):
        Actions(self.marionette).long_press(self.root_element, 2).perform()

        self.marionette.switch_to_frame()
        self.wait_for_element_displayed(*self._modal_dialog_ok_locator)
        modal_dialog_message = self.marionette.find_element(*self._modal_dialog_message_locator).text

        app_name = modal_dialog_message[
            modal_dialog_message.find('Add') + 3:
            modal_dialog_message.find('to Home Screen?')
        ].strip()  # TODO remove hack after Bug 845828 lands in V1-train
        self.marionette.find_element(*self._modal_dialog_ok_locator).tap()

        return app_name
