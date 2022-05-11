from rest_framework.renderers import BrowsableAPIRenderer


class CustomBrowsableAPIRenderer(BrowsableAPIRenderer):
    """Overrides the standard DRF Browsable API renderer."""

    def get_context(self, *args, **kwargs):
        context = super(CustomBrowsableAPIRenderer, self).get_context(*args, **kwargs)
        # Remove "HTML" tabs
        context["post_form"] = None
        context["put_form"] = None
        context["raw_data_post_form"] = None
        return context
