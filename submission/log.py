import logging


class IPAddressFilter(logging.Filter):
    def filter(self, record):
        if hasattr(record, 'request'):
            x_forwarded_for = record.request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                record.ip = x_forwarded_for.split(',')[0]
            else:
                record.ip = record.request.META.get('REMOTE_ADDR')
        if hasattr(record, 'ident'):
            record.ip = record.ident
        return True


class NameFilter(logging.Filter):
    def filter(self, record):
        if "submission_lib" in record.name:
            record.name = record.name.replace("submission_lib.", "drm_lib.")
        else:
            record.name = record.name.replace("submission.", "")
        return True
