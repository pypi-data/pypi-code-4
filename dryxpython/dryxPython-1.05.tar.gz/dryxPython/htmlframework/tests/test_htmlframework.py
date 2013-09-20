import os
import nose
from .. import htmlframework

## SETUP AND TEARDOWN FIXTURE FUNCTIONS FOR THE ENTIRE MODULE
def setUpModule():
    import logging
    import logging.config
    import yaml

    "set up test fixtures"
    moduleDirectory = os.path.dirname(__file__) + "/tests"

    # SETUP PATHS TO COMMONG DIRECTORIES FOR TEST DATA
    global pathToInputDataDir, pathToOutputDir, pathToOutputDataDir, pathToInputDir
    pathToInputDir = moduleDirectory+"/input/"
    pathToInputDataDir = pathToInputDir + "data/"
    pathToOutputDir = moduleDirectory+"/output/"
    pathToOutputDataDir = pathToOutputDir+"data/"

    # SETUP THE TEST LOG FILE
    global testlog
    testlog = open(pathToOutputDir + "tests.log", 'w')

    # SETUP LOGGING
    loggerConfig = """
    version: 1
    formatters:
        file_style:
            format: '* %(asctime)s - %(name)s - %(levelname)s (%(filename)s > %(funcName)s > %(lineno)d) - %(message)s  '
            datefmt: '%Y/%m/%d %H:%M:%S'
        console_style:
            format: '* %(asctime)s - %(levelname)s: %(filename)s:%(funcName)s:%(lineno)d > %(message)s'
            datefmt: '%H:%M:%S'
        html_style:
            format: '<div id="row" class="%(levelname)s"><span class="date">%(asctime)s</span>   <span class="label">file:</span><span class="filename">%(filename)s</span>   <span class="label">method:</span><span class="funcName">%(funcName)s</span>   <span class="label">line#:</span><span class="lineno">%(lineno)d</span> <span class="pathname">%(pathname)s</span>  <div class="right"><span class="message">%(message)s</span><span class="levelname">%(levelname)s</span></div></div>'
            datefmt: '%Y-%m-%d <span class= "time">%H:%M <span class= "seconds">%Ss</span></span>'
    handlers:
        console:
            class: logging.StreamHandler
            level: DEBUG
            formatter: console_style
            stream: ext://sys.stdout
    root:
        level: DEBUG
        handlers: [console]"""

    logging.config.dictConfig(yaml.load(loggerConfig))
    global log
    log = logging.getLogger(__name__)

    # x-setup-dbconn-for-test-module

    return None

def tearDownModule():
    "tear down test fixtures"
    # CLOSE THE TEST LOG FILE
    testlog.close()
    return None

class emptyLogger:
    info=None
    error=None
    debug=None
    critical=None
    warning=None


class test_mediaObject():
    def test_mediaObject_works_as_expected(self):
        kwargs = {}
        kwargs["displayType"]='div'
        kwargs["img"]=''
        kwargs["headlineText"]=''
        kwargs["nestedMediaObjects"]=False
        dfh.mediaObject(**kwargs)
#    """ Generate an abstract object style for building various types of components (like blog comments, Tweets, etc) that feature a left- or right-aligned image alongside textual content.
#
#    **Key Arguments:**
#        - ``displayType`` -- the display style of the media object [ "div" | "li" ]
#        - ``img`` -- the image to include
#        - ``headlineText`` -- the headline text for the object
#        - ``nestedMediaObjects`` -- nested media objects to be appended
#
#    **Return:**
#        - ``media`` -- the media object
#    """
class test_well():
    def test_well_works_as_expected(self):
        kwargs = {}
        kwargs["wellText"]=''
        wellSize='default'
        dfh.well(**kwargs)
#    """Get well. Use the well as a simple effect on an element to give it an inset effect.
#
#    **Key Arguments:**
#        - ``wellText`` -- the text to be displayed in the well
#        - ``wellSize`` -- the size of the well [ "default" | "large" | "small" ]
#
#    **Return:**
#        - ``well`` -- the well
#    """
class test_closeIcon():
    def test_closeIcon_works_as_expected(self):
        kwargs = {}
        dfh.closeIcon(**kwargs)
#    """Get close icon. The generic close icon for dismissing content like modals and alerts.
#
#    **Key Arguments:**
#
#    **Return:**
#        - ``closeIcon`` -- the closeIcon
#    """
class test_get_button():
    def test_get_button_works_as_expected(self):
        kwargs = {}
        kwargs["size"]="large",
        kwargs["block"]=False,
        kwargs["color"]="blue",
        kwargs["text"]="button",
        kwargs["htmlId"]=False,
        kwargs["htmlClass"]=False,
        kwargs["extraAttr"]=False,
        kwargs["disabled"]=False
        dfh.get_button(**kwargs)
#    """The button method (bases on the twitter bootstrap buttons)
#
#    **Key Arguments:**
#        - ``size`` - button size - mini, small, default, large
#        - ``block`` - block button?
#        - ``color`` - color
#        - ``text`` - button text
#        - ``htmlId`` -- the name of the button
#        - ``htmlClass`` -- the class of the button
#        - ``disabled`` -- disable the button if true (flatten & unclickable)
#
#    **Return:**
#        - ``button``
#    """
class test_button():
    def test_button_works_as_expected(self):
        kwargs = {}
        kwargs["buttonText"]="",
        kwargs["buttonStyle"]="default",
        kwargs["buttonSize"]="default",
        kwargs["href"]=False,
        kwargs["submit"]=False,
        kwargs["block"]=False,
        kwargs["disable"]=False
        dfh.button(**kwargs)

#    """Generate a button - TBS style
#
#    **Key Arguments:**
#        - ``buttonText`` -- the text to display on the button
#        - ``buttonStyle`` -- the style of the button required [ default | primary | info | success | warning | danger | inverse | link ]
#        - ``buttonSize`` -- the size of the button required [ large | small | mini ]
#        - ``href`` -- link the button to another location?
#        - ``submit`` -- set to true if a form button [ true | false ]#
#        - ``block`` -- create block level buttons?those that span the full width of a parent [ True | False ]
#        - ``disable`` -- this class is only for aesthetic; you must use custom JavaScript to disable links here
#
#    **Return:**
#        - ``button`` -- the button
#    """

class test_buttonGroup():
    def test_buttonGroup_works_as_expected(self):
        kwargs = {}
        kwargs["buttonList"]="",
        kwargs["format"]="default"
        dfh.buttonGroup(**kwargs)
#    """Generate a buttonGroup - TBS style
#
#    **Key Arguments:**
#        - ``buttonList`` -- a list of buttons
#        - ``format`` -- format of the button [ default | toolbar | vertical ]
#
#    **Return:**
#        - ``buttonGroup`` -- the buttonGroup
#    """
class test_code():
    def test_code_works_as_expected(self):
        kwargs = {}
        kwargs["content"]="",
        kwargs["inline"]=True,
        kwargs["scroll"]=False
        dfh.code(**kwargs)
#    """Generate a code section
#
#    **Key Arguments:**
#        - ``content`` -- the content of the code block
#        - ``inline`` -- inline or block?
#        - ``scroll`` -- give the block a scroll bar on y-axis?
#
#    **Return:**
#        - ``code`` -- the code section
#    """
class test_get_dropdown_menu_for():
    def test_get_dropdown_menu_for_works_as_expected(self):
        kwargs = {}
        dbConn, log, menuName, title, linkList
        dfh.get_dropdown_menu_for(**kwargs)
#  """Generate a dropdown menu with the provided list of links.
#
#  **Key Arguments:**
#    - ``dbConn`` -- mysql database connection
#    - ``log`` -- logger
#    - ``menuName`` -- the name of the menu
#    - ``title`` -- the title of the menu
#    - ``linkList`` -- a list of links that the menu should display
#
#  **Return:**
#    - ``menu`` -- the dropdown menu
#  """
class test_get_option_list():
    def test_get_option_list_works_as_expected(self):
        kwargs = {}
        kwargs["optionList"]=["one","two","three","four","five"]
        dfh.get_option_list(**kwargs)
#  """Create a dropdown option list
#
#    **Key Arguments:**
#        - ``optionList`` -- list of items to appear in option list
#        - ``attributeDict`` -- dictionary of the following keywords:
#        - ``htmlClass`` -- the html element class
#        - ``htmlId`` -- the html element id
#        - ``blockContent`` -- actual content to be placed in html code block
#        - ``jsEvents`` -- inline javascript events
#        - ``extraAttr`` -- extra inline css attributes and/or handles
#        - ``name`` -- an extra hook (much like "id")
#        - ``type`` -- HTML input types = color, date, datetime, datetime-local, email, month, number, range, search, tel, time, url, week
#        - ``placeholder`` -- text to be displayed by default in the input box
#        - ``required`` -- make input required (boolean)
#        - ``autofocus`` -- make this the auofocus element of the form (i.e. place cursor here)
#        - ``maxlength`` -- maximum character length for the form
#
#    **Returns:**
#        - ``block`` -- the HTML code block
#  """
class test_dropdown():
    def test_dropdown_works_as_expected(self):
        kwargs = {}
        kwargs["buttonSize"]="default",
        kwargs["color"]="grey",
        kwargs["menuTitle"]="#",
        kwargs["splitButton"]=False,
        kwargs["linkList"]=[],
        kwargs["separatedLinkList"]=False,
        kwargs["pull"]=False,
        kwargs["direction"]="down",
        kwargs["onPhone"]=True,
        kwargs["onTablet"]=True,
        kwargs["onDesktop"]=True
        dfh.dropdown(**kwargs)




#    """get a toggleable, contextual menu for displaying lists of links. Made interactive with the dropdown JavaScript plugin. You need to wrap the dropdown's trigger and the dropdown menu within .dropdown, or another element that declares position: relative;
#
#    - ``buttonSize`` -- size of button [ mini | small | default | large ]
#    - ``buttonColor`` -- [ default | sucess | error | warning | info ]
#    - ``menuTitle`` -- the title of the menu
#    - ``splitButton`` -- split the button into a separate action button and a dropdown
#    - ``linkList`` -- a list of (linked) items items that the menu should display
#    - ``separatedLinkList`` -- a list of (linked) items items that the menu should display below divider
#    - ``pull`` -- [ false | right | left ] (e.g Add ``right`` to a ``.dropdown-menu`` to right align the dropdown menu.)
#    - ``direction`` -- drop [ down | up ]
#    - ``onPhone`` -- does this container get displayed on a phone sized screen
#    - ``onTablet`` -- does this container get displayed on a tablet sized screen
#    - ``onDesktop`` -- does this container get displayed on a desktop sized screen
#
#      **Return:**
#        - ``dropdown`` -- the dropdown menu
#    """
class test_get_fieldset():
    def test_get_fieldset_works_as_expected(self):
        kwargs = {}
        kwargs["htmlClass"]="test"
        kwargs["htmlId"]="test"
        kwargs["blockContent"]="test"
        kwargs["jsEvents"]="test"
        kwargs["extraAttr"]="test"
        kwargs["legend"]="test"
        attributeDict=kwargs
        dfh.get_fieldset(**attributeDict)
#  """Create a ``fieldset`` HTML code block with legend
#
#  **Key Arguments:**
#    - ``attributeDict`` -- dictionary of the following keywords:
#    - ``htmlClass`` -- the html element class
#    - ``htmlId`` -- the html element id
#    - ``blockContent`` -- actual content to be placed in html code block
#    - ``jsEvents`` -- inline javascript event
#    - ``extraAttr`` -- extra incline css attributes and/or handles
#    - ``legend`` -- fieldset legend
#
#  **Return:**
#    - ``block``
#
#  attributeDict template -- dict(htmlClass=___,
#                                  kwargs["htmlId"]=___,
#                                  kwargs["jsEvents"]=___,
#                                  kwargs["extraAttr"]=___,
#                                  kwargs["blockContent"]=___,
#                                  kwargs["legend"]=___
#                                )
#  """
class test_get_input_block():
    def test_get_input_block_works_as_expected(self):
        kwargs = {}
        kwargs["tag"]="test"
        kwargs["htmlClass"]="test"
        kwargs["htmlId"]="test"
        kwargs["blockContent"]="test"
        kwargs["jsEvents"]="test"
        kwargs["extraAttr"]="test"
        kwargs["name"]="test"
        kwargs["type"]="test"
        kwargs["placeholder"]="test"
        kwargs["required"]="test"
        kwargs["autofocus"]="test"
        kwargs["maxlength"]="test"
        kwargs["row"]="test"
        attributeDict=kwargs
        dfh.get_input_block(**attributeDict)
#  """The HTML5 input tag used mainly in forms
#
#  **Key Arguments:**
#    - ``attributeDict`` -- dictionary of the following keywords:
#    - ``tag`` -- input, textarea
#    - ``htmlClass`` -- the html element class
#    - ``htmlId`` -- the html element id
#    - ``blockContent`` -- actual content to be placed in html code block
#    - ``jsEvents`` -- inline javascript event
#    - ``extraAttr`` -- extra incline css attributes and/or handles
#    - ``name`` -- an extra hook (much like "id")
#    - ``type`` -- HTML input types = color, date, datetime, datetime-local, email, month, number, range, search, tel, time, url, week
#    - ``placeholder`` -- text to be displayed by default in the input box
#    - ``required`` -- make input required (boolean)
#    - ``autofocus`` -- make this the auofocus element of the form (i.e. place cursor here)
#    - ``maxlength`` -- maximum character length for the form
#    - ``row`` -- number of rows for a *textarea* (i.e. height of the textbox)
#
#  **Returns**
#    - ``block`` -- the input HTML code block
#
#  attributeDict template --
#      dict(
#            kwargs["tag"]=___,
#            kwargs["htmlClass"]=___,
#            kwargs["htmlId"]=___,
#            kwargs["jsEvents"]=___,
#            kwargs["extraAttr"]=___,
#            kwargs["blockContent"]=___,
#            kwargs["name"]=___,
#            kwargs["type"]=___,
#            kwargs["placeholder"]=___,
#            kwargs["required"]=___,
#            kwargs["autofocus"]=___,
#            kwargs["maxlength"]=___,
#            kwargs["row"]=___,
#            kwargs["value"]=___
#          )
#  """
class test_searchForm():
    def test_searchForm_works_as_expected(self):
        kwargs = {}
        kwargs["buttonText"]="",
        kwargs["span"]=2,
        kwargs["inlineHelpText"]=False,
        kwargs["blockHelpText"]=False,
        kwargs["focusedInput"]=False
        dfh.searchForm(**kwargs)
#    """Generate a search-form - TBS style
#
#    **Key Arguments:**
#        - ``buttonText`` -- the button text
#        - ``span`` -- column span
#        - ``inlineHelpText`` -- inline and block level support for help text that appears around form controls
#        - ``blockHelpText`` -- a longer block of help text that breaks onto a new line and may extend beyond one line
#        - ``focusedInputText`` -- make the input focused by providing some initial editable input text
#
#    **Return:**
#        - ``searchForm`` -- the search-form
#    """
class test_form():
    def test_form_works_as_expected(self):
        kwargs = {}
        kwargs["content"]="",
        kwargs["formType"]="inline",
        kwargs["navBarPull"]=False
        dfh.form(**kwargs)
#    """Generate a form - TBS style
#
#    **Key Arguments:**
#        - ``content`` -- the content
#        - ``formType`` -- the type if the form required [ "inline" | "horizontal" | "search" | "navbar-form" | "navbar-search" ]
#        - ``navBarPull`` -- align the form is in a navBar [ false | right | left ]
#
#    **Return:**
#        - ``inlineForm`` -- the inline form
#    """
class test_horizontalFormControlGroup():
    def test_horizontalFormControlGroup_works_as_expected(self):
        kwargs = {}
        kwargs["content"]="",
        kwargs["validationLevel"]=False
        dfh.horizontalFormControlGroup(**kwargs)
#    """Generate a horizontal form control group (row) - TBS style
#
#    **Key Arguments:**
#        - ``content`` -- the content
#        - ``validationLevel`` -- validation level [ warning | error | info | success ]
#
#    **Return:**
#        - ``horizontalFormControlGroup`` -- the horizontal form control group
#    """
class test_horizontalFormControlLabel():
    def test_horizontalFormControlLabel_works_as_expected(self):
        kwargs = {}
        kwargs["labelText"]="",
        kwargs["forId"]=False
        dfh.horizontalFormControlLabel(**kwargs)
#    """Generate a horizontal form control label  - TBS style
#
#    **Key Arguments:**
#        - ``labelText`` -- the label text
#        - ``forId`` -- what is the label for (id of the associated object)?
#
#    **Return:**
#        - ``horizontalFormRowLabel`` -- the horizontalFormRowLabel
#    """
class test_formInput():
    def test_formInput_works_as_expected(self):
        kwargs = {}
        kwargs["ttype"]="text",
        kwargs["placeholder"]="",
        kwargs["span"]=2,
        kwargs["searchBar"]=False,
        kwargs["pull"]=False,
        kwargs["prepend"]=False,
        kwargs["append"]=False,
        button1=False,
        button2=False,
        kwargs["appendDropdown"]=False,
        kwargs["inlineHelpText"]=False,
        kwargs["blockHelpText"]=False,
        kwargs["focusedInput"]=False,
        kwargs["required"]=False,
        kwargs["disabled"]=False
        dfh.formInput(**kwargs)
#
#    """Generate a form input - TBS style
#
#    **Key Arguments:**
#        - ``ttype`` -- [ text | password | datetime | datetime-local | date | month | time | week | number | email | url | search | tel | color ]
#        - ``placeholder`` -- the placeholder text
#        - ``span`` -- column span
#        - ``searchBar`` -- is this input a searchbar?
#        - ``pull`` -- [ false | right | left ] align form
#        - ``prepend`` -- prepend text to the input.
#        - ``append`` -- append text to the input.
#        - ``button1`` -- do you want a button associated with the input?
#        - ``button2`` -- as above for a 2nd button
#        - ``appendDropdown`` -- do you want a appended button-dropdown associated with the input?
#        - ``prependDropdown`` -- do you want a prepended button-dropdown associated with the input?
#        - ``inlineHelpText`` -- inline and block level support for help text that appears around form controls
#        - ``blockHelpText`` -- a longer block of help text that breaks onto a new line and may extend beyond one line
#        - ``focusedInputText`` -- make the input focused by providing some initial editable input text
#        - ``required`` -- required attribute if the field is not optional
#        - ``disabled`` -- add the disabled attribute on an input to prevent user input
#
#    **Return:**
#        - ``input`` -- the input
#    """
class test_textarea():
    def test_textarea_works_as_expected(self):
        kwargs = {}
        kwargs["rows"]="",
        kwargs["span"]=2,
        kwargs["inlineHelpText"]=False,
        kwargs["blockHelpText"]=False,
        kwargs["focusedInputText"]=False,
        kwargs["required"]=False,
        kwargs["disabled"]=False
        dfh.textarea(**kwargs)
#    """Generate a textarea - TBS style
#
#    **Key Arguments:**
#        - ``rows`` -- the number of rows the text area should span
#        - ``span`` -- column span
#        - ``inlineHelpText`` -- inline and block level support for help text that appears around form controls
#        - ``blockHelpText`` -- a longer block of help text that breaks onto a new line and may extend beyond one line
#        - ``focusedInputText`` -- make the input focused by providing some initial editable input text
#        - ``required`` -- required attribute if the field is not optional
#        - ``disabled`` -- add the disabled attribute on an input to prevent user input
#
#    **Return:**
#        - ``textarea`` -- the textarea
#    """
class test_checkbox():
    def test_checkbox_works_as_expected(self):
        kwargs = {}
        kwargs["optionText"]="",
        kwargs["inline"]=False,
        kwargs["optionNumber"]=1,
        kwargs["inlineHelpText"]=False,
        kwargs["blockHelpText"]=False,
        kwargs["disabled"]=False
        dfh.checkbox(**kwargs)
#    """Generate a checkbox - TBS style
#
#    **Key Arguments:**
#        - ``optionText`` -- the text associated with this checkbox
#        - ``inline`` -- display the checkboxes inline?
#        - ``optionNumber`` -- option number of inline
#        - ``inlineHelpText`` -- inline and block level support for help text that appears around form controls
#        - ``blockHelpText`` -- a longer block of help text that breaks onto a new line and may extend beyond one line
#        - ``disabled`` -- add the disabled attribute on an input to prevent user input
#
#    **Return:**
#        - ``checkbox`` -- the checkbox
#    """
class test_select():
    def test_select_works_as_expected(self):
        kwargs = {}
        kwargs["optionList"]=[],
        kwargs["multiple"]=False,
        kwargs["span"]=2,
        kwargs["inlineHelpText"]=False,
        kwargs["blockHelpText"]=False,
        kwargs["required"]=False,
        kwargs["disabled"]=False
        dfh.select(**kwargs)
#    """Generate a select - TBS style
#
#    **Key Arguments:**
#        - ``optionList`` -- the list of options
#        - ``multiple`` -- display all the options at once?
#        - ``span`` -- column span
#        - ``inlineHelpText`` -- inline and block level support for help text that appears around form controls
#        - ``blockHelpText`` -- a longer block of help text that breaks onto a new line and may extend beyond one line
#        - ``required`` -- required attribute if the field is not optional
#        - ``disabled`` -- add the disabled attribute on an input to prevent user input
#
#    **Return:**
#        - ``select`` -- the select
#    """
class test_radio():
    def test_radio_works_as_expected(self):
        kwargs = {}
        kwargs["optionText"]="",
        kwargs["optionNumber"]=1,
        kwargs["inlineHelpText"]=False,
        kwargs["blockHelpText"]=False,
        kwargs["disabled"]=False
        dfh.radio(**kwargs)
#    """Generate a radio - TBS style
#
#    **Key Arguments:**
#        - ``optionText`` -- the text associated with this checkbox
#        - ``optionNumber`` -- the order in the option list
#        - ``inlineHelpText`` -- inline and block level support for help text that appears around form controls
#        - ``blockHelpText`` -- a longer block of help text that breaks onto a new line and may extend beyond one line
#        - ``disabled`` -- add the disabled attribute on an input to prevent user input
#
#    **Return:**
#        - ``radio`` -- the radio
#    """
class test_controlRow():
    def test_controlRow_works_as_expected(self):
        kwargs = {}
        kwargs["inputList"]=[]
        dfh.controlRow(**kwargs)
#    """Generate a control-row - TBS style
#
#    **Key Arguments:**
#        - ``inputList`` -- list of inputs for the control row
#
#    **Return:**
#        - ``controlRow`` -- the controlRow
#    """
class test_uneditableInput():
    def test_uneditableInput_works_as_expected(self):
        kwargs = {}
        kwargs["placeholder"]="",
        kwargs["span"]=2,
        kwargs["inlineHelpText"]=False,
        kwargs["blockHelpText"]=False
        dfh.uneditableInput(**kwargs)
#    """Generate a uneditableInput - TBS style
#
#    **Key Arguments:**
#        - ``placeholder`` -- the placeholder text
#        - ``span`` -- column span
#        - ``inlineHelpText`` -- inline and block level support for help text that appears around form controls
#        - ``blockHelpText`` -- a longer block of help text that breaks onto a new line and may extend beyond one line
#
#    **Return:**
#        - ``uneditableInput`` -- an uneditable input - the user can see but not interact
#    """
class test_formActions():
    def test_formActions_works_as_expected(self):
        kwargs = {}
        kwargs["primaryButton"]="",
        button2=False,
        button3=False,
        button4=False,
        button5=False,
        kwargs["inlineHelpText"]=False,
        kwargs["blockHelpText"]=False
        dfh.formActions(**kwargs)
#    """Generate a formActions - TBS style
#
#    **Key Arguments:**
#        - ``primaryButton`` -- the primary button
#        - ``button2`` -- another button
#        - ``button3`` -- another button
#        - ``button4`` -- another button
#        - ``button5`` -- another button
#        - ``inlineHelpText`` -- inline and block level support for help text that appears around form controls
#        - ``blockHelpText`` -- a longer block of help text that breaks onto a new line and may extend beyond one line
#
#    **Return:**
#        - ``formActions`` -- the formActions
#    """

###################################################################
# CLASSES                                                         #
###################################################################

###################################################################
# PUBLIC FUNCTIONS                                                #
###################################################################
# xxx-replace
## LAST MODIFIED : May 28, 2013
## CREATED : May 28, 2013
## AUTHOR : DRYX
class test_unescape_html():
    def test_unescape_html_works_as_expected(self):
        kwargs = {}
        dbConn, log, html
        dfh.unescape_html(**kwargs)
#    """Unescape a string previously escaped with cgi.escape()
#
#    **Key Arguments:**
#        - ``dbConn`` -- mysql database connection
#        - ``log`` -- logger
#        - ``html`` -- the string to be unescaped
#
#    **Return:**
#        - ``html`` -- the unescaped string
#    """
class test_image():
    def test_image_works_as_expected(self):
        kwargs = {}
        kwargs["src"]="http://placehold.it/200x200",
        kwargs["href"]=False,
        kwargs["display"]="False", # [ rounded | circle | polaroid ]
        kwargs["pull"]="left", # [ "left" | "right" | "center" ]
        kwargs["htmlClass"]=False,
        kwargs["thumbnail"]=False,
        kwargs["width"]=False,
        kwargs["onPhone"]=True,
        kwargs["onTablet"]=True,
        kwargs["onDesktop"]=True
        dfh.image(**kwargs)
#    """Create an HTML image (with ot without link).
#    Based on the Twitter bootstrap setup.
#
#    **Key Arguments:**
#        - ``src`` -- image url
#        - ``href`` -- image link url
#        - ``display`` -- how the image is to be displayed [ rounded | circle | polaroid ]
#        - ``pull`` -- how to align the image if within a <div> [ "left" | "right" | "center" ]
#        - ``htmlClass`` -- the class of the row
#        - ``width`` -- the width of the image
#        - ``onPhone`` -- does this container get displayed on a phone sized screen
#        - ``onTablet`` -- does this container get displayed on a tablet sized screen
#        - ``onDesktop`` -- does this container get displayed on a desktop sized screen
#
#    **Return:**
#        - ``image`` - the formatted image
#    """
class test_thumbnail():
    def test_thumbnail_works_as_expected(self):
        kwargs = {}
        kwargs["htmlContent"]=""
        dfh.thumbnail(**kwargs)
#    """Generate a thumbnail - TBS style
#
#    **Key Arguments:**
#        - ``htmlContent`` -- the html content of the thumbnail
#
#    **Return:**
#        - ``thumbnail`` -- the thumbnail with HTML content
#    """
class test_label():
    def test_label_works_as_expected(self):
        kwargs = {}
        kwargs["text"]=''
        level='default'
        dfh.label(**kwargs)
#    """ Generate a label - TBS style
#
#    **Key Arguments:**
#        - ``text`` -- the text content
#        - ``level`` -- the level colour of the label [ "default" | "success" | "warning" | "important" | "info" | "inverse" ]
#
#    **Return:**
#        - ``label`` -- the label
#    """
class test_badge():
    def test_badge_works_as_expected(self):
        kwargs = {}
        kwargs["text"]=''
        level='default'
        dfh.badge(**kwargs)
#    """ Generate a badge - TBS style
#
#    **Key Arguments:**
#        - ``text`` -- the text content
#        - ``level`` -- the level colour of the badge [ "default" | "success" | "warning" | "important" | "info" | "inverse" ]
#
#    **Return:**
#        - ``badge`` -- the badge
#    """
class test_alert():
    def test_alert_works_as_expected(self):
        kwargs = {}
        kwargs["alertText"]=''
        kwargs["alertHeading"]=""
        kwargs["extraPadding"]=False
        kwargs["alertLevel"]="warning"
        dfh.alert(**kwargs)

#    """ Generate a alert - TBS style
#
#    **Key Arguments:**
#        - ``alertText`` -- the text to be displayed in the alert
#        - ``extraPadding`` -- for longer messages, increase the padding on the top and bottom of the alert wrapper
#        - ``alertLevel`` -- the level of the alert [ "warning" | "error" | "success" | "info" ]
#
#    **Return:**
#        - ``alert`` -- the alert
#    """
class test_progressBar():
    def test_progressBar_works_as_expected(self):
        kwargs = {}
        kwargs["barStyle"]="plain",
        kwargs["precentageWidth"]="10",
        kwargs["barLevel"]="info"
        dfh.progressBar(**kwargs)
#    """Generate a progress bar - TBS style
#
#    **Key Arguments:**
#        - ``barStyle`` -- style of the progress bar [ "plain" | "stripped" | "stripped-active" ]
#        - ``precentageWidth`` -- the current progress of the bar
#        - ``barLevel`` -- the level color of the bar [ "info" | "warning" | "success" | "error" ]
#
#    **Return:**
#        - ``progressBar`` -- the progressBar
#    """
class test_stackedProgressBar():
    def test_stackedProgressBar_works_as_expected(self):
        kwargs = {}
        kwargs["barStyle"]="plain",
        kwargs["infoWidth"]="10",
        kwargs["successWidth"]="10",
        kwargs["warningWidth"]="10",
        kwargs["errorWidth"]="10"

        dfh.stackedProgressBar(**kwargs)
#    """Generate a progress bar - TBS style
#
#    **Key Arguments:**
#        - ``barStyle`` -- style of the progress bar [ "plain" | "stripped" | "stripped-active" ]
#        - ``infoWidth`` -- the precentage width of the info level bar
#        - ``successWidth`` -- the precentage width of the success level bar
#        - ``warningWidth`` -- the precentage width of the warning level bar
#        - ``errorWidth`` -- the precentage width of the error level bar
#
#    **Return:**
#        - ``progressBar`` -- the progressBar
#    """
class test_responsive_navigation_bar():
    def test_responsive_navigation_bar_works_as_expected(self):
        kwargs = {}

    kwargs["shade"]='dark',
    kwargs["brand"]=False,
    kwargs["outsideNavList"]=False,
    kwargs["insideNavList"]=False,
    kwargs["htmlId"]=False,
    kwargs["onPhone"]=True,
    kwargs["onTablet"]=True,
    kwargs["onDesktop"]=True,
    dfh.responsive_navigation_bar(**kwargs)
#    """ Create a twitter bootstrap responsive nav-bar component
#
#    **Key Arguments:**
#        - ``shade`` -- if dark then colors are inverted [ False | 'dark' ]
#        - ``brand`` -- the website brand [ image | text ]
#        - ``outsideNavList`` -- nav-list to be contained outside collapsible content
#        - ``insideNavList`` -- nav-list to be contained inside collapsible content
#        - ``htmlId`` --
#        - ``onPhone`` -- does this container get displayed on a phone sized screen
#        - ``onTablet`` -- does this container get displayed on a tablet sized screen
#        - ``onDesktop`` -- does this container get displayed on a desktop sized screen
#
#    **Return:**
#        - ``navBar`` --
#    """
class test_nav_list():
    def test_nav_list_works_as_expected(self):
        kwargs = {}

    kwargs["itemList"]=[],
    kwargs["pull"]=False,
    kwargs["onPhone"]=True,
    kwargs["onTablet"]=True,
    kwargs["onDesktop"]=True,
    dfh.nav_list(**kwargs)
#    """Create an html list of navigation items from the required python list
#
#    **Key Arguments:**
#        - ``itemList`` -- items to be included in the navigation list
#        - ``pull`` -- float the nav-list [ False | 'right' | 'left' ]
#        - ``onPhone`` -- does this container get displayed on a phone sized screen
#        - ``onTablet`` -- does this container get displayed on a tablet sized screen
#        - ``onDesktop`` -- does this container get displayed on a desktop sized screen
#
#    **Return:**
#        - navList
#    """
class test_get_nav_block():
    def test_get_nav_block_works_as_expected(self):
        kwargs = {}
        kwargs["htmlClass"]="test"
        kwargs["htmlId"]="test"
        kwargs["blockContent"]="test"
        kwargs["jsEvents"]="test"
        kwargs["extraAttr"]="test"
        attributeDict=kwargs
        dfh.get_nav_block(**attributeDict)
#  """Create a basic ``<nav>`` code block
#
#  **Variable Attributes:**
#    - ``attributeDict`` -- dictionary of the following keywords:
#    - ``htmlClass`` -- the html element class
#    - ``htmlId`` -- the html element id
#    - ``blockContent`` -- actual content to be placed in html code block
#    - ``jsEvents`` -- inline javascript event
#    - ``extraAttr`` -- extra inline css attributes and/or handles
#
#  **Returns:**
#    - ``block`` -- the html block
#
#  attributeDict template:
#    attributeDict = dict(
#                          kwargs["htmlClass"]=___,
#                          kwargs["htmlId"]=___,
#                          kwargs["jsEvents"]=___,
#                          kwargs["extraAttr"]=___,
#                          kwargs["blockContent"]=___
#                        )
#  """
class test_searchbox():
    def test_searchbox_works_as_expected(self):
        kwargs = {}

    kwargs["size"]='medium',
    kwargs["placeHolder"]=False,
    kwargs["button"]=False,
    kwargs["buttonSize"]='small',
    kwargs["buttonColor"]='grey',
    kwargs["navBar"]=False,
    kwargs["pull"]=False,
    dfh.searchbox(**kwargs)
#    """Create a Search box
#
#    **Key Arguments:**
#        - ``size`` -- size = mini | small | medium | large | xlarge | xxlarge
#        - ``placeholder`` -- placeholder text
#        - ``button`` -- do you want a search button?
#        - ``buttonSize``
#        - ``buttonColor``
#
#    **Return:**
#        - ``markup`` -- markup for the searchbar
#    """
class test_tabbableNavigation():
    def test_tabbableNavigation_works_as_expected(self):
        kwargs = {}

    kwargs["contentDictionary"]={},
    kwargs["fadeIn"]=True,
    kwargs["direction"]='top',
    dfh.tabbableNavigation(**kwargs)
#    """ Generate a tabbable Navigation
#
#    **Key Arguments:**
#        - ``contentDictionary`` -- the content dictionary { name : content }
#        - ``fadeIn`` -- make tabs fade in
#        - ``direction`` -- the position of the tabs [ above | below | left | right ]
#
#    **Return:**
#        - ``tabbableNavigation`` -- the tabbableNavigation
#    """
class test_navBar():
    def test_navBar_works_as_expected(self):
        kwargs = {}
        kwargs["brand"]='',
        kwargs["contentDictionary"]={},
        kwargs["dividers"]=False,
        kwargs["fixedOrStatic"]=False,
        kwargs["location"]='top',
        kwargs["responsive"]=False,
        kwargs["dark"]=False
        dfh.navBar(**kwargs)
#    """ Generate a navBar - TBS style
#
#    **Key Arguments:**
#        - ``brand`` -- the website brand [ image | text ]
#        - ``contentDictionary`` -- the content dictionary { text : href }
#        - ``fixedOrStatic`` -- Fix the navbar to the top or bottom of the viewport, or create a static full-width navbar that scrolls away with the page [ False | fixed | static ]
#        - ``location`` -- location of the navigation bar if fixed or static
#        - ``dark`` -- Modify the look of the navbar by making it dark
#
#    **Return:**
#        - ``navBar`` -- the navBar
#    """
class test_pagination():
    def test_pagination_works_as_expected(self):
        kwargs = {}
        kwargs["listItems"]="",
        kwargs["size"]="default",
        kwargs["align"]="left"
        dfh.pagination(**kwargs)
#    """Generate pagination - TBS style. Simple pagination inspired by Rdio, great for apps and search results.
#
#    **Key Arguments:**
#        - ``listItems`` -- the numbered items to be listed within the <ul> of the pagination block
#        - ``size`` -- additional pagination block sizes [ "mini" | "small" | "default" | "large" ]
#        - ``align`` -- change the alignment of pagination links [ "left" | "center" | "right" ]
#
#    **Return:**
#        - ``pagination`` -- the pagination
#    """
class test_htmlDocument():
    def test_htmlDocument_works_as_expected(self):
        kwargs = {}
        kwargs["content"]=''
        dfh.htmlDocument(**kwargs)
#    """The doctype and html tags
#
#    **Key Arguments:**
#        - ``content`` -- the head and body of the html page
#
#    **Return:**
#        - ``doctype`` -- the HTML5 doctype
#    """
class test_head():
    def test_head_works_as_expected(self):
        kwargs = {}

    kwargs["relativeUrlBase"]='',
    kwargs["mainCssFileName"]="main.css",
    kwargs["pageTitle"]="",
    kwargs["extras"]="",
    dfh.head(**kwargs)
#    """Generate an html head element for your webpage
#
#    **Key Arguments:**
#        ``relativeUrlBase`` -- relative base url for js, css, image folders
#        ``pageTitle`` -- well, the page title!
#        ``mainCssFileName`` -- css file name
#        ``extras`` -- any extra info to be included in the ``head`` element
#
#    **Return:**
#        - ``head`` -- the head
#    """
class test_body():
    def test_body_works_as_expected(self):
        kwargs = {}
        kwargs["navBar"]=False,
        kwargs["content"]="",
        kwargs["htmlId"]="",
        kwargs["extraAttr"]="",
        kwargs["relativeUrlBase"]="",
        kwargs["responsive"]=True,
        kwargs["googleAnalyticsCode"]=False,
        kwargs["jsFileName"]="main.js"

        dfh.body(**kwargs)
#    """Generate an HTML body
#
#    **Key Arguments:**
#        - ``navBar`` -- the top navigation bar
#        - ``htmlId`` -- *id* attribute of the body
#        - ``content`` -- body content built from smaller HTML code blocks
#        - ``extraAttr`` -- an extra attributes to be added to the body definition
#        - ``relativeUrlBase`` -- how to get back to the document root
#        - ``responsive`` -- should the webpage be responsive to screen-size?
#        - ``googleAnalyticsCode`` -- google analytics code for the website
#        - ``jsFileName`` -- the name of the main javascript file
#
#    **Return:**
#        - ``body`` -- the body
#    """
class test_row():
    def test_row_works_as_expected(self):
        kwargs = {}
        kwargs["responsive"]=True,
        kwargs["columns"]='',
        kwargs["htmlId"]=False,
        kwargs["htmlClass"]=False,
        kwargs["onPhone"]=True,
        kwargs["onTablet"]=True,
        kwargs["onDesktop"]=True,
        dfh.row(**kwargs)
#    """Create a row using the Twitter Bootstrap static layout grid.
#    The static Bootstrap grid system utilizes 12 columns.
#
#    **Key Arguments:**
#        - ``responsive`` -- fluid layout if true, fixed if false
#        - ``columns`` -- coulmns to be included in this row
#        - ``htmlId`` -- the id of the row
#        - ``htmlClass`` -- the class of the row
#        - ``onPhone`` -- does this row get displayed on a phone sized screen
#        - ``onTablet`` -- does this row get displayed on a tablet sized screen
#        - ``onDesktop`` -- does this row get displayed on a desktop sized screen
#
#    **Return:**
#        - ``row`` -- the row
#    """
class test_get_simple_div():
    def test_get_simple_div_works_as_expected(self):
        kwargs = {}
        kwargs["htmlId"]=None
        blockContent=None
        dfh.get_simple_div(**kwargs)
#    """ Generate a basic <div> with block-content
#
#  ****Key Arguments:****
#    - ``htmlId`` -- the html id attribute
#    - ``blockContent`` -- content to be surrounded by html div tag
#
#  **Return:**
#    - ``div``
#    """
class test_get_javascript_block():
    def test_get_javascript_block_works_as_expected(self):
        kwargs = {}
        kwargs["jsPath"]="test"
        dfh.get_javascript_block(**kwargs)
#    """ Create a javascript *<script>* html code block
#
#  ****Key Arguments:****
#    - ``jsPath`` -- path the js file
#
#  **Return:**
#    - ``block`` -- HTML code block
#    """
class test_get_html_block():
    def test_get_html_block_works_as_expected(self):
        kwargs = {}
        kwargs["tag"]="test"
        kwargs["htmlClass"]="test"
        kwargs["htmlId"]="test"
        kwargs["href"]="test"
        kwargs["blockContent"]="test"
        kwargs["jsEvents"]="test"
        kwargs["extraAttr"]="test"
        kwargs["src"]="test"
        kwargs["alt"]="test"
        kwargs["action"]="test"
        kwargs["method"]="test"
        kwargs["type"]="test"
        attributeDict=kwargs
        dfh.get_html_block(**attributeDict)
#    """Get an HTML code block (tag) which in turn can be meshed together to build webpages.
#
#    **Variable Attributes:**
#      - ``attributeDict`` -- dictionary with the following keywords:
#      - ``tag`` -- the html tag (a, div, span ...)
#      - ``htmlClass`` -- the html element class
#      - ``htmlId`` -- the html element id
#      - ``href`` -- linked url
#      - ``blockContent`` -- actual content to be placed in html code block
#      - ``jsEvents`` -- inline javascript event
#      - ``extraAttr`` -- extra incline css attributes and/or handles
#      - ``src`` -- source for images
#      - ``alt`` -- alternative text for images
#      - ``action`` -- action used in forms
#      - ``method`` -- method used in forms
#      - ``type`` -- type of object
#
#    **Returns:**
#      - ``block`` -- the html block
#
#    attributeDict template -- dict(tag=___,
#                                    htmlClass:divVerticalKids/divHorizontalKids,
#                                    kwargs["htmlId"]=___,
#                                    kwargs["jsEvents"]=___,
#                                    kwargs["extraAttr"]=___,
#                                    kwargs["blockContent"]=___,
#                                    kwargs["href"]=___,
#                                    kwargs["src"]=___,
#                                    kwargs["alt"]=___,
#                                    kwargs["action"]=___,
#                                    kwargs["method"]=___,
#                                    kwargs["type"]=___
#                                  )
#    """
class test_grid_column():
    def test_grid_column_works_as_expected(self):
        kwargs = {}
        kwargs["log"]=log
        kwargs["span"]=1,
        kwargs["offset"]=0,
        kwargs["content"]='',
        kwargs["htmlId"]=False,
        kwargs["htmlClass"]=False,
        kwargs["onPhone"]=True,
        kwargs["onTablet"]=True,
        kwargs["onDesktop"]=True,
        dfh.grid_column(**kwargs)
#    """ Get a column block for the Twiiter Bootstrap static layout grid.
#
#    **Key Arguments:**
#        - ``log`` -- logger
#        - ``span`` -- the relative width of the column
#        - ``offset`` -- increase the left margin of the column by this amount
#        - ``htmlId`` -- the id of the column
#        - ``htmlClass`` -- the class of the column
#        - ``onPhone`` -- does this column get displayed on a phone sized screen
#        - ``onTablet`` -- does this column get displayed on a tablet sized screen
#        - ``onDesktop`` -- does this column get displayed on a desktop sized screen
#
#    **Return:**
#        - ``column`` -- the column
#            """
class test__container():
    def test__container_works_as_expected(self):
        kwargs = {}
        kwargs["responsive"]=True,
        kwargs["content"]='',
        kwargs["htmlId"]=False,
        kwargs["htmlClass"]=False,
        kwargs["onPhone"]=True,
        kwargs["onTablet"]=True,
        kwargs["onDesktop"]=True,
        dfh._container(**kwargs)
#    """ The over-all content container for the twitter bootstrap webpage
#
#    **Key Arguments:**
#        - ``responsive`` -- fluid layout if true, fixed if false
#        - ``content`` -- html content of the container div
#        - ``htmlId`` -- the id of the container
#        - ``htmlClass`` -- the class of the container
#        - ``onPhone`` -- does this container get displayed on a phone sized screen
#        - ``onTablet`` -- does this container get displayed on a tablet sized screen
#        - ``onDesktop`` -- does this container get displayed on a desktop sized screen
#
#    **Return:**
#        - None
#        """
class test_tr():
    def test_tr_works_as_expected(self):
        kwargs = {}
        kwargs["cellContent"]="",
        kwargs["color"]=False
        dfh.tr(**kwargs)
#    """Generate a table row - TBS style
#
#    **Key Arguments:**
#        - ``cellContent`` -- the content - either <td>s or <th>s
#        - ``color`` -- [ sucess | error | warning | info ]
#
#    **Return:**
#        - ``tr`` -- the table row
#    """
class test_th():
    def test_th_works_as_expected(self):
        kwargs = {}
        kwargs["content"]="",
        kwargs["color"]=False
        dfh.th(**kwargs)
#    """Generate a table header cell - TBS style
#
#    **Key Arguments:**
#        - ``content`` -- the content
#        - ``color`` -- [ sucess | error | warning | info ]
#
#    **Return:**
#        - ``th`` -- the table header cell
#    """
class test_td():
    def test_td_works_as_expected(self):
        kwargs = {}
        kwargs["content"]="",
        kwargs["color"]=False
        dfh.td(**kwargs)
#    """Generate a table data cell - TBS style
#
#    **Key Arguments:**
#        - ``content`` -- the content
#        - ``color`` -- [ sucess | error | warning | info ]
#
#    **Return:**
#        - ``td`` -- the table data cell
#    """
class test_tableCaption():
    def test_tableCaption_works_as_expected(self):
        kwargs = {}
        kwargs["content"]=""
        dfh.tableCaption(**kwargs)
#    """Generate a table caption - TBS style
#
#    **Key Arguments:**
#        - ``content`` -- the content
#
#    **Return:**
#        - ``tableCaption`` -- the table caption
#    """
class test_thead():
    def test_thead_works_as_expected(self):
        kwargs = {}
        kwargs["trContent"]=""
        dfh.thead(**kwargs)
#    """Generate a table head - TBS style
#
#    **Key Arguments:**
#        - ``trContent`` -- the table row content
#
#    **Return:**
#        - ``thead`` -- the table head
#    """
class test_tbody():
    def test_tbody_works_as_expected(self):
        kwargs = {}
        kwargs["trContent"]=""
        dfh.tbody(**kwargs)
#    """Generate a table body - TBS style
#
#    **Key Arguments:**
#        - ``trContent`` -- the table row content
#
#    **Return:**
#        - ``tbody`` -- the table body
#    """
class test_table():
    def test_table_works_as_expected(self):
        kwargs = {}
        kwargs["caption"]="",
        kwargs["thead"]="",
        kwargs["tbody"]="",
        kwargs["stripped"]=True,
        kwargs["bordered"]=False,
        kwargs["hover"]=True,
        kwargs["condensed"]=False
        dfh.table(**kwargs)
#    """Generate a table - TBS style
#
#    **Key Arguments:**
#        - ``caption`` -- the table caption
#        - ``thead`` -- the table head
#        - ``tbody`` -- the table body
#        - ``stripped`` -- Adds zebra-striping to any odd table row
#        - ``bordered`` -- Add borders and rounded corners to the table.
#        - ``hover`` -- Enable a hover state on table rows within a <tbody>
#        - ``condensed`` -- Makes tables more compact by cutting cell padding in half.
#
#    **Return:**
#        - ``table`` -- the table
#    """
class test_p():
    def test_p_works_as_expected(self):
        kwargs = {}
        kwargs["content"]="",
        kwargs["lead"]=False,
        kwargs["textAlign"]=False,
        kwargs["color"]=False,
        kwargs["navBar"]=False,
        kwargs["onPhone"]=True,
        kwargs["onTablet"]=True,
        kwargs["onDesktop"]=True
        dfh.p(**kwargs)
#    """Get a Paragraph element
#
#    **Key Arguments:**
#        - ``content`` -- content of the paragraph
#        - ``lead`` -- is this a lead paragraph?
#        - ``textAlign`` -- how to align paragraph text [ left | center | right ]
#        - ``color`` -- colored text for emphasis [ muted | warning | info | error | success ]
#        - ``navBar`` -- is this <p> for a navbar?
#        - ``onPhone`` -- does this container get displayed on a phone sized screen
#        - ``onTablet`` -- does this container get displayed on a tablet sized screen
#        - ``onDesktop`` -- does this container get displayed on a desktop sized screen
#
#    **Return:**
#        - ``p`` -- the html paragraph element
#    """
class test_emphasizeText():
    def test_emphasizeText_works_as_expected(self):
        kwargs = {}
        kwargs["style"]="em",
        kwargs["text"]=""
        dfh.emphasizeText(**kwargs)
#    """Get HTML's default emphasis tags with lightweight styles.
#
#    **Key Arguments:**
#        - ``style`` -- the emphasis tag [ "small" | "strong" | "em" ]
#        - ``text`` -- the text to emphasise
#
#    **Return:**
#        - ``emphasizeText`` -- the emphasized text
#    """
class test_abbr():
    def test_abbr_works_as_expected(self):
        kwargs = {}
        kwargs["abbreviation"]="",
        kwargs["fullWord"]=""
        dfh.abbr(**kwargs)
#    """Get HTML5 Abbreviation
#
#    **Key Arguments:**
#        - ``abbreviation`` -- the abbreviation
#        - ``fullWord`` -- the full word
#
#    **Return:**
#        - abbr
#    """
class test_address():
    def test_address_works_as_expected(self):
        kwargs = {}
        kwargs["name"]=False,
        addressLine1=False,
        addressLine2=False,
        addressLine3=False,
        kwargs["phone"]=False,
        kwargs["email"]=False,
        kwargs["twitterHandle"]=False
        dfh.address(**kwargs)
#    """Get The HTML5 address element
#
#    **Key Arguments:**
#        - ``name`` -- name of person
#        - ``addressLine1`` -- first line of the address
#        - ``addressLine2`` -- second line of the address
#        - ``addressLine3`` -- third line of the address
#        - ``phone`` -- telephone number
#        - ``email`` -- email address
#        - ``twitterHandle`` -- twitter handle
#
#    **Return:**
#        - address
#    """
class test_blockquote():
    def test_blockquote_works_as_expected(self):
        kwargs = {}
        kwargs["content"]="",
        kwargs["source"]=False,
        kwargs["pullRight"]=False
        dfh.blockquote(**kwargs)
#    """Get HTML5 Blockquote
#
#    **Key Arguments:**
#        - ``content`` -- content to be quoted
#        - ``source`` -- source of quote
#
#    **Return:**
#        - None
#    """
class test_ul():
    def test_ul_works_as_expected(self):
        kwargs = {}
        kwargs["itemList"]=[],
        kwargs["unstyled"]=False,
        kwargs["inline"]=False,
        kwargs["dropDownMenu"]=False,
        kwargs["navStyle"]=False,
        kwargs["navPull"]=False,
        kwargs["navDirection"]="horizontal",
        kwargs["breadcrumb"]=False,
        kwargs["pager"]=False,
        kwargs["thumbnails"]=False,
        kwargs["mediaList"]=False

        dfh.ul(**kwargs)
#    """Get An unordered list -- can be used for navigation, stacked tab and pill
#
#    **Key Arguments:**
#        - ``itemList`` -- a list of items to be included in the unordered list
#        - ``unstyled`` -- is the list to be unstyled (first children only)
#        - ``inline`` -- place all list items on a single line with inline-block and some light padding.
#        - ``dropDownMenu`` -- is this ul to be used in a dropdown menu? [ false | true ]
#        - ``navStyle`` -- set the navigation style if used for tabs & pills etc [ nav | tabs | pills | list ]
#        - ``navPull`` -- set the alignment of the navigation links [ false | left | right ]
#        - ``navDirection`` -- set the direction of the navigation [ 'default' | 'stacked' ]
#        - ``breadcrumb`` -- display breadcrumb across muliple pages? [ False | True ]
#        - ``pager`` -- use <ul> for a pager
#        - ``thumbnails`` -- use the <ul> for a thumnail block?
#        - ``mediaList`` -- use the <ul> for a media object list?
#
#    **Return:**
#        - ul
#    """
class test_li():
    def test_li_works_as_expected(self):
        kwargs = {}
        kwargs["content"]="",
        kwargs["span"]=False,
        kwargs["disabled"]=False,
        kwargs["submenuTitle"]=False,
        kwargs["divider"]=False,
        kwargs["navStyle"]=False,
        kwargs["navDropDown"]=False,
        kwargs["pager"]=False
        dfh.li(**kwargs)
#    """Generate a li - TBS style
#
#    **Key Arguments:**
#        - ``content`` -- the content (if a subMenu for dropdown this should be <ul>)
#        - ``span`` -- the column span [ False | 1-12 ]
#        - ``disabled`` -- add the disabled attribute on an grey out this list item. Note you can optionally swap anchors for spans to remove click functionality.
#        - ``submenuTitle`` -- if a submenu (<ul>) is to be included as content, use this as the title.
#        - ``divider`` -- if true this list item shall be a line
#        - ``navStyle`` -- how is the navigation element to be displayed? [ active | header ]
#        - ``navDropDown`` -- true if the list item is to be used as a dropdown in navigation
#        - ``pager`` -- use the <li> within a pager navigation? [ False | "previous" | "next" ]
#
#    **Return:**
#        - ``li`` -- the li
#    """
class test_a():
    def test_a_works_as_expected(self):
        kwargs = {}
        kwargs["content"]="",
        kwargs["href"]=False,
        kwargs["tableIndex"]=False,
        kwargs["triggerStyle"]=False
        dfh.a(**kwargs)
#    """Generate an anchor - TBS style
#
#    **Key Arguments:**
#        - ``content`` -- the content
#        - ``href`` -- the href link for the anchor
#        - ``tableIndex`` -- table index for the dropdown menus [ False | -1 ]
#        - ``triggerStyle`` -- link to be used as a dropDown or tab trigger? [ False | "dropdown" | "tab" ]
#
#
#    **Return:**
#        - ``a`` -- the a
#    """
class test_ol():
    def test_ol_works_as_expected(self):
        kwargs = {}
        kwargs["itemList"]=[]
        dfh.ol(**kwargs)
#    """An ordered list
#
#    **Key Arguments:**
#        - ``itemList`` -- a list of items to be included in the ordered list
#
#    **Return:**
#        - ol
#    """
class test_descriptionLists():
    def test_descriptionLists_works_as_expected(self):
        kwargs = {}
        kwargs["orderedDictionary"]={},
        kwargs["sideBySide"]=False
        dfh.descriptionLists(**kwargs)
#    """A list of definitions.
#
#    **Key Arguments:**
#        - ``orderedDictionary`` -- the ordered dictionary of the terms and their definitions
#        - ``sideBySide`` -- Make terms and descriptions in <dl> line up side-by-side.
#
#    **Return:**
#        - None
#    """
class test_code():
    def test_code_works_as_expected(self):
        kwargs = {}
        kwargs["content"]="",
        kwargs["inline"]=True,
        kwargs["scroll"]=False
        dfh.code(**kwargs)
#    """Generate a code section
#
#    **Key Arguments:**
#        - ``content`` -- the content of the code block
#        - ``inline`` -- inline or block?
#        - ``scroll`` -- give the block a scroll bar on y-axis?
#
#    **Return:**
#        - ``code`` -- the code section
#    """
class test_heroUnit():
    def test_heroUnit_works_as_expected(self):
        kwargs = {}
        kwargs["headline"]="",
        kwargs["tagline"]="",
        kwargs["buttonStyle"]="primary",
        kwargs["buttonText"]=""

        dfh.heroUnit(**kwargs)
#    """Generate a heroUnit - TBS style
#
#    **Key Arguments:**
#        - ``headline`` -- the headline text
#        - ``tagline`` -- the tagline text for below the headline
#        - ``buttonStyle`` -- the style of the button to be used
#        - ``buttonText`` -- the text for the button
#        - ``buttonHref`` -- the anchor link for the button
#
#    **Return:**
#        - ``heroUnit`` -- the heroUnit
#    """
class test_pageHeader():
    def test_pageHeader_works_as_expected(self):
        kwargs = {}
        kwargs["headline"]="",
        kwargs["tagline"]=""
        dfh.pageHeader(**kwargs)
#    """Generate a pageHeader - TBS style
#
#    **Key Arguments:**
#        - ``headline`` -- the headline text
#        - ``tagline`` -- the tagline text for below the headline
#
#    **Return:**
#        - ``pageHeader`` -- the pageHeader
#    """

