from sirep.conf import get_setting

SHOW_ADMIN_TEST_MODEL_DEMO = get_setting('SHOW_ADMIN_TEST_MODEL_DEMO')

if SHOW_ADMIN_TEST_MODEL_DEMO is True:
    import sirep

    from sirep.models import TestModel

    # Define the report class
    class TestReport(sirep.Report):
        verbose_name = 'Test report'
        fields = [u'ID', u'Title', u'Counter', u'Username', u'E-mail']
        items = []
        limit = 200
        date_field = 'date_published'
        queryset = TestModel._default_manager.filter().select_related('user')

        def process_data(self):
            queryset = self.get_queryset()

            self.items = []
            for a in queryset:
                self.items.append([
                    a.pk,
                    a.title,
                    a.counter,
                    a.user.username if a.user else '',
                    a.user.email if a.user else ''
                    ])

    # Register the report
    sirep.register('test-report', TestReport)