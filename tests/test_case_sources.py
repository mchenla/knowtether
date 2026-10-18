import contextlib
import csv
import importlib.util
import io
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch


class HistoricalSourceTests(unittest.TestCase):
    def test_unmeasured_format_count_is_omitted_and_missing_measured_count_rejected(self):
        repo=Path(__file__).resolve().parents[1]
        spec=importlib.util.spec_from_file_location('case_builder',repo/'scripts/prepare_mechanism_cases.py')
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);(root/'examples').mkdir()
            for name in ['adaptive-0.5.0-results.json','paired-0.4.1-results.json']:
                shutil.copyfile(repo/'examples'/name,root/'examples'/name)
            with patch.object(module,'ROOT',root),contextlib.redirect_stdout(io.StringIO()):
                module.main()
                report=root/'examples/mechanism-work/work-report/records.csv'
                self.assertNotIn('long_dash_ranges',next(csv.reader(io.StringIO(report.read_text()))))
                context=json.loads((report.parent/'context.json').read_text())
                self.assertIn('not measured',context['measurement'])
                source=root/'examples/paired-0.4.1-results.json'
                data=json.loads(source.read_text(encoding='utf-8'))
                del data['results'][0]['raw_numeric_long_dash_count']
                source.write_text(json.dumps(data),encoding='utf-8')
                with self.assertRaises(KeyError):module.main()
