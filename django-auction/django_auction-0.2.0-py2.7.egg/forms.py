from django import forms
import auction.models
from auction.utils.generic import get_or_create_bidbasket
from auction.models import Lot

class BidForm(forms.Form):
    amount = forms.DecimalField()
    lot_id = forms.IntegerField()

    def save_bid(self, request):
        lot_id = self.data.get('lot_id')
        amount = self.data.get('amount')

        lot = self.get_lot(lot_id)

        bidbasket = get_or_create_bidbasket(request)
        if bidbasket:
            return bidbasket.add_bid(lot, amount)
        return False

    def get_lot(self, lot_id):
        """
        For simplified extending.
        """
        #return auction.models.Lot.objects.get(pk=lot_id)
        return Lot.objects.filter(is_biddable=True).get(pk=lot_id)