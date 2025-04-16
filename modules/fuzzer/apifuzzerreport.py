import six
from kitty.data.report import Report

from modules.fuzzer.utils import try_b64encode
from modules.util.loggable import Loggable as log

class ApifuzzerReport(Report):
    def __init__(self, name):
        super().__init__(None)
        self.add("name", name)


    def __getitem__(self, key):
        """
        Allow dict-like access to data fields or subreports.
        """
        if key in self._data_fields:
            return self.get(key)
        elif key in self._sub_reports:
            return self._sub_reports[key]
        else:
            raise KeyError(f"{key} not found in report fields or subreports")

    def is_failed(self):
        """
        .. deprecated:: 0.6.7
            use :func:`~kitty.data.export.Report.get_status`
        """
        raise NotImplementedError("API was changed, use get_status instead")


    def to_dict(self, encoding="base64"):
        """
        Return a dictionary version of the export

        :param encoding: required encoding for the string values (default: 'base64')
        :rtype: dictionary
        :return: dictionary representation of the export
        """
        res = {}
        for k, v in self._data_fields.items():
            if isinstance(v, (bytes, bytearray, six.string_types)):
                v = try_b64encode(v)
            res[k] = v
        for k, v in self._sub_reports.items():
            res[k] = v.to_dict(encoding)
        return res

    def from_dict(self, d):
        '''
        Construct a ``Report`` object from dictionary.

        :type d: dictionary
        :param d: dictionary representing the report
        :param encoding: encoding of strings in the dictionary (default: 'base64')
        :return: Report object
        '''
        try:
            report = ApifuzzerReport(d.get('name'))
            report.set_status(d.get('status'))
            sub_reports = d.get('sub_reports')
            del d['sub_reports']
            for k, v in d.items():
                if k in sub_reports:
                    report.add(k, Report.from_dict(v))
                else:
                    if k.lower() == 'status':
                        report.set_status(v)
                    else:
                        report.add(k, v)
        except Exception as e:
            log.error(e)

        return report