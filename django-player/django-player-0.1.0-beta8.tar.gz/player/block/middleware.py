from django.http import HttpResponse


class RenderBlockMiddleware(object):
    """This middleware render only a block if passed by request """

    def process_request(self, request):
        if 'render_block' in request.GET:
            from player.block.models import PlacedBlock

            block_id = request.GET['render_block']
            placed_block = PlacedBlock.objects.get(id=block_id)
            block = placed_block.get_block()
            return HttpResponse(block.render(
                request,
                context=dict(),
            ))
