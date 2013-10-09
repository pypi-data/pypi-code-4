from selenium import webdriver
import unittest


class SeleniumTestCase(unittest.TestCase):
    def setUp(self):
        capabilities = {
            "browserName": "chrome",
            "platform": "ANY",
        }
        self.driver = webdriver.Remote(desired_capabilities=capabilities)
        self.driver.implicitly_wait(10)
        
    def tearDown(self):
        self.driver.quit()
