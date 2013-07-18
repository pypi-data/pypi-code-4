
from Products.Collage.browser.views import BaseView

from cs.collage import collageMessageFactory as _

# XXX Copy and fix erros from Products.Collage.browser.views.RowView
class RowView(BaseView):
    def getColumnBatches(self, bsize=3):
        columns = self.context.folderlistingFolderContents()
        if not columns:
            return []

        # calculate number of batches
        count = (len(columns)-1)/bsize+1

        batches = []
        for c in range(count):
            batch = []
            for i in range(bsize):
                index = c*bsize+i

                # pad with null-columns
                column = None

                if index < len(columns):
                    column = columns[index]

                # do not pad first row
                if column or c > 0:
                    batch += [column]

            batches += [batch]

        return batches


class EqualRowView(RowView):
    title = _(u'Equal Rows')

class Last4WithImage(BaseView):
    title = _(u'Last 4 with image')
