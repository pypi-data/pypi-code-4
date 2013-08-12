from selenium import webdriver

browser_mapping = {"firefox": webdriver.Firefox,
                    "chrome": webdriver.Chrome,
                    "ie": webdriver.Ie,
                    "opera" : webdriver.Opera,
                    "remote": webdriver.Remote,
                    "phantomjs": webdriver.PhantomJS,
                    "iphone" : webdriver.Remote,
                    "ipad": webdriver.Remote,
                    "android": webdriver.Remote}

#:
capabilities = {"firefox": webdriver.DesiredCapabilities.FIREFOX,
                "chrome": webdriver.DesiredCapabilities.CHROME,
                "ie": webdriver.DesiredCapabilities.INTERNETEXPLORER,
                "opera": webdriver.DesiredCapabilities.OPERA,
                "phantomjs":webdriver.DesiredCapabilities.PHANTOMJS,
                "iphone":webdriver.DesiredCapabilities.IPHONE,
                "ipad":webdriver.DesiredCapabilities.IPAD,
                "android":webdriver.DesiredCapabilities.ANDROID}

