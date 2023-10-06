from rest_framework.renderers import BrowsableAPIRenderer

from rest_framework import renderers


class PlainTextRenderer(renderers.BaseRenderer):
    media_type = 'text/plain'
    format = 'text'

    def render(self, data, media_type=None, renderer_context=None):
        return str(renderers.JSONRenderer().render(data, media_type, renderer_context)).encode(self.charset)


class CustomBrowsableAPIRenderer(BrowsableAPIRenderer):
    """Overrides the standard DRF Browsable API renderer."""

    def get_context(self, *args, **kwargs):
        context = super(CustomBrowsableAPIRenderer, self).get_context(*args, **kwargs)
        # Remove "HTML" tabs
        context["post_form"] = None
        context["put_form"] = None
        context["raw_data_post_form"] = None
        return context
