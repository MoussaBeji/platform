from rest_framework.renderers import BaseRenderer


class ZIPRenderer(BaseRenderer):
    media_type = 'application/zip'
    format = 'zip'
    charset = None
    render_style = 'binary'

    def render(self, data, media_type=None, renderer_context=None):
        return data