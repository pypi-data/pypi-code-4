from Products.Faq.content import FaqFolder
from Products.Faq.content import FaqEntry

import sys
sys.modules['Products.Faq.FaqFolder'] = FaqFolder
sys.modules['Products.Faq.FaqEntry'] = FaqEntry

