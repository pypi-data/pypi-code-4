from ftw.upgrade import UpgradeStep


class FixParagraphMimetypes(UpgradeStep):

    def __call__(self):
        title = 'Fix broken mimetype of Paragraph objects without text'
        query = {'portal_type': 'Paragraph'}

        for paragraph in self.objects(query, title):
            field = paragraph.Schema().get('text')
            if field.getContentType(paragraph) == 'text/html':
                continue

            field.setContentType(paragraph, 'text/html')
