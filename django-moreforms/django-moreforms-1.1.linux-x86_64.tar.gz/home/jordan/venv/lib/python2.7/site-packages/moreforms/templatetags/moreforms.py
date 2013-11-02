from django import template
from django.utils.safestring import SafeString

register = template.Library()

@register.simple_tag
def auto_submit(label='...'):
    return SafeString('''<script type="text/javascript">
        $(document).ready(function(){
            $("select, input").change(function(){
                $(this).closest("form").submit();
            });
        });
    </script>
    <noscript>
        <input class='is-js' type='submit' value='&#9100; Undo' name='undo'>
        <input class='is-js' type='submit' value='Continue &#187;' name='continue'>
    </noscript>''')
    