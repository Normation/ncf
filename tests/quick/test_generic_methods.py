#!/usr/bin/python3
"""
Sanity test file for methods
"""

import sys
import os
DIRNAME = os.path.dirname(os.path.abspath(__file__))
TESTLIB_PATH = DIRNAME + '/../testlib'
sys.path.insert(0, TESTLIB_PATH)
import re
import unittest
import collections
import testlib
import avocado

class TestNcfBundles(avocado.Test):
    """
    Sanity tests for methods
    """
    def setUp(self):
        """
        Tests setup
        """
        self.methods = testlib.get_methods()

    def test_deprecated_bundle_calls(self):
        """
        Methods should not call deprecated methods
        """
        deprecated_methods = [x.get_bundle_name()
                              for x in self.methods if 'deprecated' in x.metadata]

        for method in self.methods:
            with self.subTest(i=method.path):
                for line in method.content:
                    match = re.match(
                        r'\s*usebundle\s*=>\s*([a-zA-Z_]+)\s*.*$', line, flags=re.UNICODE
                    )
                    if match:
                        self.assertNotIn(match.group(1), deprecated_methods)
    def test_methods_should_have_a_metadata(self):
        """
        Methods should have a metadata
        """
        for method in self.methods:
            with self.subTest(i=method.path):
                self.assertIn('name', method.metadata)
                self.assertIn('description', method.metadata)
                # We have way too much method without documentation at the moment
                # this will need a dedicated pr
                #self.assertIn('documentation', method.metadata)
                self.assertIn('parameter', method.metadata)
                self.assertIn('class_prefix', method.metadata)
                self.assertIn('class_parameter', method.metadata)

    def test_methods_should_have_only_one_agent_bundle(self):
        """
        Methods should define a unique agent bundle
        """
        for method in self.methods:
            with self.subTest(i=method.path):
                bundles = method.get_bundles()
                self.assertEqual(1, len(bundles))

    def test_methods_name_should_be_unique(self):
        """
        Methods should @name should be unique
        """
        names = [x.metadata['name'] for x in self.methods]
        duplicates = [x for x, y in collections.Counter(names).items() if y > 1]
        if [] != duplicates:
            for method in self.methods:
                with self.subTest(i=method.path):
                    self.assertNotIn(method.metadata['name'], duplicates)

    def test_old_class_prefix(self):
        """
        Methods should define an old_class_prefix in either one of the following formats:
          "old_class_prefix" string => canonify("<class_prefix_from_metadata>_${<class_parameter_from_metadata>}");
          "old_class_prefix" string => "<class_prefix_from_metadata>_${canonified_<class_parameter_from_metadata>}";

        In fact, we should force the first one.
        """
        for method in self.methods:
            with self.subTest(k=method.path):
                class_prefix = method.metadata['class_prefix']
                class_parameter = method.metadata['class_parameter']

                class_pattern1 = r"\"old_class_prefix\"\s+string\s+=>\s+canonify\(\"" + class_prefix + "_" + r"\${" + class_parameter + r"}\"\);"
                class_pattern2 = r"\"old_class_prefix\"\s+string\s+=>\s+\"" + class_prefix + "_" + r"\${canonified_" + class_parameter + r"}\";"

                if not skip(method):
                    self.assertTrue(testlib.test_pattern_on_file(method.path, class_pattern1) is not None or testlib.test_pattern_on_file(method.path, class_pattern2) is not None)


    def test_class_prefix(self):
        """
        Methods should define a class_prefix, which is verified in the cfengine acceptance tests.
        Here we only verify that the 'args' variable used to define the class_prefix is the list
        of all canonified parameters defined in the metadata, in the same order

          "args" slist => { "<arg1>", "<arg2>", etc... };

        """
        for method in self.methods:
            with self.subTest(i=method.path):
                params = r",\s*".join([r"\"\${" + x.strip() + r"}\"" for x in method.metadata['bundle_args']])
                class_prefix_pattern = r"\s+\"args\"\s+slist\s+=>\s+\{\s*" + params + r"\s*\};"
                if not skip(method):
                    self.assertTrue(testlib.test_pattern_on_file(method.path, class_prefix_pattern) is not None)

    @avocado.skip('Some methods are still using _log')
    def test_methods_should_use_latest_logger(self):
        """
        Methods should always use the latest logger available
        Currently not applied since some methods are using _log instead for some reasons
        """
        for method in self.methods:
            logger_pattern = r'.*usebundle\s+=>\s+_log_v3.*'
            with self.subTest(i=method.path):
                if not skip(method):
                    self.assertTrue(testlib.test_pattern_on_file(method.path, logger_pattern) is not None)

    def test_methods_should_not_contain_unescaped_chars(self):
        """
        Test if the documentation fields contain unescaped dollar characters that would break pdflatex
        """
        for method in self.methods:
            check_backquotes = re.compile(r'[^\`]*\$[^\`]*')
            with self.subTest(i=method.path):
                if 'documentation' in method.metadata:
                    self.assertFalse(check_backquotes.match(method.metadata['documentation']))

    def test_methods_name_should_be_bundle_name(self):
        """
        Methods filename should be base on their name
        """
        for method in self.methods:
            with self.subTest(i=method.path):
                bundle_name = method.get_bundle_name()
                filename = method.path_basename
                compared_filename = re.sub(r'[0-9]+', '', filename)
                self.assertTrue(bundle_name == compared_filename, '\nbundle_name = %s\n  filename = %s'%(bundle_name, filename))

    @avocado.skip('Lots of methods are not correct atm')
    def test_methods_name_should_be_class_prefix(self):
        """
        Methods prefix should be based on their name
        """
        for method in self.methods:
            with self.subTest(i=method.path):
                class_prefix = method.metadata['class_prefix']
                path = method.path_basename
                self.assertTrue(class_prefix == path, '\nprefix = %s\n  path = %s'%(class_prefix, path))

    def test_methods_shouldi_not_use_deprecated_loggers(self):
        """
        Methods should never use deprecated helper bundles/bodies
        """
        deprecated_bundles = ['_logger_default', '_logger']
        deprecated_bodies = [
            'do_if_immediate',
            'classes_generic_return_codes',
            'kept_if_else',
            'kept_if_else_persist',
            'ncf_ensure_section_content',
            'rudder_delete_if_not_in_list',
            'rudder_section_selector',
            'rudder_empty_select',
            'noempty_backup',
            'empty_backup',
            'cp',
            'rudder_copy_from',
            'copy_digest',
            'u_p',
            'rudder_common_minutes_old',
            'rudder_debian_knowledge',
            'rudder_rpm_knowledge',
            'yum_rpm_no_version',
            'redhat_local_install',
            'redhat_install',
            'debian_local_install',
            'ncf_generic',
            'ncf_generic_version',
            'apt_get_version',
            'rudder_rug',
            'rudder_yum',
            'cron_bin'
        ]
        for method in self.methods:
            with self.subTest(i=method.path):
                bodies_matching = [x for x in deprecated_bodies if '"%s"'%x in method.raw_content]
                self.assertEqual(bodies_matching, [], "%s contains deprecated bodies %s"%(method.path, bodies_matching))

                bundle_regex = '(' + '|'.join(deprecated_bundles) + ')'
                bundle_pattern = r'.*usebundle\s+=>\s+%s.*'%bundle_regex
                matches = re.findall(bundle_pattern, method.raw_content, flags=re.UNICODE)
                self.assertEqual(matches, [], method.path + ' contains deprecated bundles ' + str(matches))

### Helper functions
def skip(method):
    """
    In some tests, we need to skip some methods, either because they are not really a true method
    and only a wrapper or because their inner logic make them exceptions
    """
    to_skip = ['file_from_shared_folder', 'user_password_hash']
    result = False
    if testlib.test_pattern_on_file(method.path, r'{\s+methods:\s+[^;]+;\s+}'):
        result = True
    elif method.path_basename in to_skip:
        result = True
    if result:
        pass
    return result

