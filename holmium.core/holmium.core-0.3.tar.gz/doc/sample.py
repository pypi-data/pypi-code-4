from holmium.core import Page,Section,Element,Elements,ElementMap,Locators*


class SampleSection(Section):
    element = Element(Locators.CSS_SELECTOR, "test")
    elements = Elements(Locators.CSS_SELECTOR, "test")


class Sample(Page):
    element = Element(Locators.CSS_SELECTOR, "test")
    elements = Elements(Locators.CSS_SELECTOR, "test")
    element_map= ElementMap(Locators.CSS_SELECTOR, "test")
    section = SampleSection(Locators.CSS_SELECTOR, "test")
