from axf.ractive import RactiveWidget
from tw2.core import Param, JSLink


class AjaxManagePhotos(RactiveWidget):
    action = Param('Url used to save newly uploaded photos', request_local=False)
    delete_action = Param('Url used to delete uploaded photos', request_local=False)
    resources = [JSLink(modname=__name__, filename='resources/formdata.js')]
    ractive_params = ['action', 'delete_action']

    ractive_template = '''
<div>
    {{#photos}}
    <div class="photo" intro="fade">
        <div class="photo-delete" on-tap="request_delete">&#10799;</div>
        <div class="photo-picture" data-photo-uid="{{uid}}" on-tap="request_upload">
            <img src="{{url}}"/>
        </div>
    </div>
    {{/photos}}
    <div class="photo photo-upload" on-tap="request_upload"></div>
</div>
'''

    ractive_init = '''
function(options) {
    if (this._super !== undefined) this._super(options);

    this.on({
      request_delete: function(click_evt) {
        var self = this;

        var xhr = new XMLHttpRequest();
        xhr.open('DELETE', makeURLWithParameter(self.get('delete_action'), "uid", click_evt.context.uid), true);
        xhr.setRequestHeader("Cache-Control", "no-cache");
        xhr.setRequestHeader("X-Requested-With", "XMLHttpRequest");

        xhr.onload = function() {
            var result = JSON.parse(this.responseText);
            self.set('photos', result.photos);
        }

        xhr.send();
      },
      request_upload: function(click_evt) {
        var self = this;

        var filefield = document.createElement('input');
        filefield.type = "file";
        filefield.name = "picture";
        filefield.onchange = function() {
            var data = new FormData();
            data.append('file', filefield.files[0]);

            if (click_evt.context.uid)
                data.append('uid', click_evt.context.uid);

            var xhr = new XMLHttpRequest();
            xhr.open('POST', self.get('action'), true);
            xhr.setRequestHeader("Cache-Control", "no-cache");
            xhr.setRequestHeader("X-Requested-With", "XMLHttpRequest");

            xhr.onload = function() {
                var result = JSON.parse(this.responseText);
                self.set('photos', result.photos);
            }

            if (data.fake) {
               xhr.setRequestHeader("Content-Type", "multipart/form-data; boundary="+ data.boundary);
               xhr.sendAsBinary(data.toString());
            } else {
               xhr.send(data);
            }
        };

        filefield.click();
      }
    });
}'''

