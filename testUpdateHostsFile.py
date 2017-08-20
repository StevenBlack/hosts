#!/usr/bin/env python

# Script by gfyoung
# https://github.com/gfyoung
#
# Python script for testing updateHostFiles.py

from updateHostsFile import (
    Colors, PY3, colorize, display_exclusion_options, exclude_domain,
    flush_dns_cache, gather_custom_exclusions, get_defaults, get_file_by_url,
    is_valid_domain_format, matches_exclusions, move_hosts_file_into_place,
    normalize_rule, path_join_robust, print_failure, print_success,
    prompt_for_exclusions, prompt_for_move, prompt_for_flush_dns_cache,
    prompt_for_update, query_yes_no, recursive_glob, remove_old_hosts_file,
    supports_color, strip_rule, update_all_sources, update_readme_data,
    write_data, write_opening_header)

import updateHostsFile
import unittest
import tempfile
import locale
import shutil
import json
import sys
import os
import re

if PY3:
    from io import BytesIO, StringIO
    import unittest.mock as mock
    unicode = str
else:
    from StringIO import StringIO
    BytesIO = StringIO
    import mock


# Test Helper Objects
class Base(unittest.TestCase):

    @staticmethod
    def mock_property(name):
        return mock.patch(name, new_callable=mock.PropertyMock)

    @property
    def sep(self):
        return "\\" if sys.platform == "win32" else "/"

    def assert_called_once(self, mock_method):
        if PY3 and sys.version_info < (3, 6):
            self.assertEqual(mock_method.call_count, 1)
        else:
            mock_method.assert_called_once()


class BaseStdout(Base):

    def setUp(self):
        sys.stdout = StringIO()

    def tearDown(self):
        sys.stdout.close()
        sys.stdout = sys.__stdout__


class BaseMockDir(Base):

    @property
    def dir_count(self):
        return len(os.listdir(self.test_dir))

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.test_dir)


def builtins():
    if PY3:
        return "builtins"
    else:
        return "__builtin__"
# End Test Helper Objects


# Project Settings
class TestGetDefaults(Base):

    def test_get_defaults(self):
        with self.mock_property("updateHostsFile.BASEDIR_PATH"):
            updateHostsFile.BASEDIR_PATH = "foo"
            actual = get_defaults()
            expected = {"numberofrules": 0,
                        "datapath": "foo" + self.sep + "data",
                        "freshen": True,
                        "replace": False,
                        "backup": False,
                        "skipstatichosts": False,
                        "keepdomaincomments": False,
                        "extensionspath": "foo" + self.sep + "extensions",
                        "extensions": [],
                        "outputsubfolder": "",
                        "hostfilename": "hosts",
                        "targetip": "0.0.0.0",
                        "sourcedatafilename": "update.json",
                        "sourcesdata": [],
                        "readmefilename": "readme.md",
                        "readmetemplate": ("foo" + self.sep +
                                           "readme_template.md"),
                        "readmedata": {},
                        "readmedatafilename": ("foo" + self.sep +
                                               "readmeData.json"),
                        "exclusionpattern": "([a-zA-Z\d-]+\.){0,}",
                        "exclusionregexs": [],
                        "exclusions": [],
                        "commonexclusions": ["hulu.com"],
                        "blacklistfile": "foo" + self.sep + "blacklist",
                        "whitelistfile": "foo" + self.sep + "whitelist"}
            self.assertDictEqual(actual, expected)
# End Project Settings


# Prompt the User
class TestPromptForUpdate(BaseStdout, BaseMockDir):

    def setUp(self):
        BaseStdout.setUp(self)
        BaseMockDir.setUp(self)

    def test_no_freshen_no_new_file(self):
        hosts_file = os.path.join(self.test_dir, "hosts")
        hosts_data = "This data should not be overwritten"

        with self.mock_property("updateHostsFile.BASEDIR_PATH"):
            updateHostsFile.BASEDIR_PATH = self.test_dir

            with open(hosts_file, "w") as f:
                f.write(hosts_data)

        for update_auto in (False, True):
            dir_count = self.dir_count
            prompt_for_update(freshen=False, update_auto=update_auto)

            output = sys.stdout.getvalue()
            self.assertEqual(output, "")

            sys.stdout = StringIO()

            self.assertEqual(self.dir_count, dir_count)

            with open(hosts_file, "r") as f:
                contents = f.read()
                self.assertEqual(contents, hosts_data)

    def test_no_freshen_new_file(self):
        hosts_file = os.path.join(self.test_dir, "hosts")

        with self.mock_property("updateHostsFile.BASEDIR_PATH"):
            updateHostsFile.BASEDIR_PATH = self.test_dir

            dir_count = self.dir_count
            prompt_for_update(freshen=False, update_auto=False)

            output = sys.stdout.getvalue()
            self.assertEqual(output, "")

            sys.stdout = StringIO()

            self.assertEqual(self.dir_count, dir_count + 1)

            with open(hosts_file, "r") as f:
                contents = f.read()
                self.assertEqual(contents, "")

    @mock.patch(builtins() + ".open")
    def test_no_freshen_fail_new_file(self, mock_open):
        for exc in (IOError, OSError):
            mock_open.side_effect = exc("failed open")

            with self.mock_property("updateHostsFile.BASEDIR_PATH"):
                updateHostsFile.BASEDIR_PATH = self.test_dir
                prompt_for_update(freshen=False, update_auto=False)

                output = sys.stdout.getvalue()
                expected = ("ERROR: No 'hosts' file in the folder. "
                            "Try creating one manually.")
                self.assertIn(expected, output)

                sys.stdout = StringIO()

    @mock.patch("updateHostsFile.query_yes_no", return_value=False)
    def test_freshen_no_update(self, _):
        hosts_file = os.path.join(self.test_dir, "hosts")
        hosts_data = "This data should not be overwritten"

        with self.mock_property("updateHostsFile.BASEDIR_PATH"):
            updateHostsFile.BASEDIR_PATH = self.test_dir

            with open(hosts_file, "w") as f:
                f.write(hosts_data)

            dir_count = self.dir_count

            update_sources = prompt_for_update(freshen=True, update_auto=False)
            self.assertFalse(update_sources)

            output = sys.stdout.getvalue()
            expected = ("OK, we'll stick with "
                        "what we've got locally.")
            self.assertIn(expected, output)

            sys.stdout = StringIO()

            self.assertEqual(self.dir_count, dir_count)

            with open(hosts_file, "r") as f:
                contents = f.read()
                self.assertEqual(contents, hosts_data)

    @mock.patch("updateHostsFile.query_yes_no", return_value=True)
    def test_freshen_update(self, _):
        hosts_file = os.path.join(self.test_dir, "hosts")
        hosts_data = "This data should not be overwritten"

        with self.mock_property("updateHostsFile.BASEDIR_PATH"):
            updateHostsFile.BASEDIR_PATH = self.test_dir

            with open(hosts_file, "w") as f:
                f.write(hosts_data)

            dir_count = self.dir_count

            for update_auto in (False, True):
                update_sources = prompt_for_update(freshen=True,
                                                   update_auto=update_auto)
                self.assertTrue(update_sources)

                output = sys.stdout.getvalue()
                self.assertEqual(output, "")

                sys.stdout = StringIO()

                self.assertEqual(self.dir_count, dir_count)

                with open(hosts_file, "r") as f:
                    contents = f.read()
                    self.assertEqual(contents, hosts_data)

    def tearDown(self):
        BaseStdout.tearDown(self)
        BaseStdout.tearDown(self)


class TestPromptForExclusions(BaseStdout):

    @mock.patch("updateHostsFile.query_yes_no", return_value=False)
    def testSkipPrompt(self, mock_query):
        gather_exclusions = prompt_for_exclusions(skip_prompt=True)
        self.assertFalse(gather_exclusions)

        output = sys.stdout.getvalue()
        self.assertEqual(output, "")

        mock_query.assert_not_called()

    @mock.patch("updateHostsFile.query_yes_no", return_value=False)
    def testNoSkipPromptNoDisplay(self, mock_query):
        gather_exclusions = prompt_for_exclusions(skip_prompt=False)
        self.assertFalse(gather_exclusions)

        output = sys.stdout.getvalue()
        expected = ("OK, we'll only exclude "
                    "domains in the whitelist.")
        self.assertIn(expected, output)

        self.assert_called_once(mock_query)

    @mock.patch("updateHostsFile.query_yes_no", return_value=True)
    def testNoSkipPromptDisplay(self, mock_query):
        gather_exclusions = prompt_for_exclusions(skip_prompt=False)
        self.assertTrue(gather_exclusions)

        output = sys.stdout.getvalue()
        self.assertEqual(output, "")

        self.assert_called_once(mock_query)


class TestPromptForFlushDnsCache(Base):

    @mock.patch("updateHostsFile.flush_dns_cache", return_value=0)
    @mock.patch("updateHostsFile.query_yes_no", return_value=False)
    def testFlushCache(self, mock_query, mock_flush):
        for prompt_flush in (False, True):
            prompt_for_flush_dns_cache(flush_cache=True,
                                       prompt_flush=prompt_flush)

            mock_query.assert_not_called()
            self.assert_called_once(mock_flush)

            mock_query.reset_mock()
            mock_flush.reset_mock()

    @mock.patch("updateHostsFile.flush_dns_cache", return_value=0)
    @mock.patch("updateHostsFile.query_yes_no", return_value=False)
    def testNoFlushCacheNoPrompt(self, mock_query, mock_flush):
        prompt_for_flush_dns_cache(flush_cache=False,
                                   prompt_flush=False)

        mock_query.assert_not_called()
        mock_flush.assert_not_called()

    @mock.patch("updateHostsFile.flush_dns_cache", return_value=0)
    @mock.patch("updateHostsFile.query_yes_no", return_value=False)
    def testNoFlushCachePromptNoFlush(self, mock_query, mock_flush):
        prompt_for_flush_dns_cache(flush_cache=False,
                                   prompt_flush=True)

        self.assert_called_once(mock_query)
        mock_flush.assert_not_called()

    @mock.patch("updateHostsFile.flush_dns_cache", return_value=0)
    @mock.patch("updateHostsFile.query_yes_no", return_value=True)
    def testNoFlushCachePromptFlush(self, mock_query, mock_flush):
        prompt_for_flush_dns_cache(flush_cache=False,
                                   prompt_flush=True)

        self.assert_called_once(mock_query)
        self.assert_called_once(mock_flush)


class TestPromptForMove(Base):

    def setUp(self):
        Base.setUp(self)
        self.final_file = "final.txt"

    def prompt_for_move(self, **move_params):
        return prompt_for_move(self.final_file, **move_params)

    @mock.patch("updateHostsFile.move_hosts_file_into_place", return_value=0)
    @mock.patch("updateHostsFile.query_yes_no", return_value=False)
    def testSkipStaticHosts(self, mock_query, mock_move):
        for replace in (False, True):
            for auto in (False, True):
                move_file = self.prompt_for_move(replace=replace, auto=auto,
                                                 skipstatichosts=True)
                self.assertFalse(move_file)

                mock_query.assert_not_called()
                mock_move.assert_not_called()

                mock_query.reset_mock()
                mock_move.reset_mock()

    @mock.patch("updateHostsFile.move_hosts_file_into_place", return_value=0)
    @mock.patch("updateHostsFile.query_yes_no", return_value=False)
    def testReplaceNoSkipStaticHosts(self, mock_query, mock_move):
        for auto in (False, True):
            move_file = self.prompt_for_move(replace=True, auto=auto,
                                             skipstatichosts=False)
            self.assertTrue(move_file)

            mock_query.assert_not_called()
            self.assert_called_once(mock_move)

            mock_query.reset_mock()
            mock_move.reset_mock()

    @mock.patch("updateHostsFile.move_hosts_file_into_place", return_value=0)
    @mock.patch("updateHostsFile.query_yes_no", return_value=False)
    def testAutoNoSkipStaticHosts(self, mock_query, mock_move):
        for replace in (False, True):
            move_file = self.prompt_for_move(replace=replace, auto=True,
                                             skipstatichosts=True)
            self.assertFalse(move_file)

            mock_query.assert_not_called()
            mock_move.assert_not_called()

            mock_query.reset_mock()
            mock_move.reset_mock()

    @mock.patch("updateHostsFile.move_hosts_file_into_place", return_value=0)
    @mock.patch("updateHostsFile.query_yes_no", return_value=False)
    def testPromptNoMove(self, mock_query, mock_move):
        move_file = self.prompt_for_move(replace=False, auto=False,
                                         skipstatichosts=False)
        self.assertFalse(move_file)

        self.assert_called_once(mock_query)
        mock_move.assert_not_called()

        mock_query.reset_mock()
        mock_move.reset_mock()

    @mock.patch("updateHostsFile.move_hosts_file_into_place", return_value=0)
    @mock.patch("updateHostsFile.query_yes_no", return_value=True)
    def testPromptMove(self, mock_query, mock_move):
        move_file = self.prompt_for_move(replace=False, auto=False,
                                         skipstatichosts=False)
        self.assertTrue(move_file)

        self.assert_called_once(mock_query)
        self.assert_called_once(mock_move)

        mock_query.reset_mock()
        mock_move.reset_mock()
# End Prompt the User


# Exclusion Logic
class TestDisplayExclusionsOptions(Base):

    @mock.patch("updateHostsFile.query_yes_no", return_value=0)
    @mock.patch("updateHostsFile.exclude_domain", return_value=None)
    @mock.patch("updateHostsFile.gather_custom_exclusions", return_value=None)
    def test_no_exclusions(self, mock_gather, mock_exclude, _):
        common_exclusions = []
        display_exclusion_options(common_exclusions, "foo", [])

        mock_gather.assert_not_called()
        mock_exclude.assert_not_called()

    @mock.patch("updateHostsFile.query_yes_no", side_effect=[1, 1, 0])
    @mock.patch("updateHostsFile.exclude_domain", return_value=None)
    @mock.patch("updateHostsFile.gather_custom_exclusions", return_value=None)
    def test_only_common_exclusions(self, mock_gather, mock_exclude, _):
        common_exclusions = ["foo", "bar"]
        display_exclusion_options(common_exclusions, "foo", [])

        mock_gather.assert_not_called()

        exclude_calls = [mock.call("foo", "foo", []),
                         mock.call("bar", "foo", None)]
        mock_exclude.assert_has_calls(exclude_calls)

    @mock.patch("updateHostsFile.query_yes_no", side_effect=[0, 0, 1])
    @mock.patch("updateHostsFile.exclude_domain", return_value=None)
    @mock.patch("updateHostsFile.gather_custom_exclusions", return_value=None)
    def test_gather_exclusions(self, mock_gather, mock_exclude, _):
        common_exclusions = ["foo", "bar"]
        display_exclusion_options(common_exclusions, "foo", [])

        mock_exclude.assert_not_called()
        self.assert_called_once(mock_gather)

    @mock.patch("updateHostsFile.query_yes_no", side_effect=[1, 0, 1])
    @mock.patch("updateHostsFile.exclude_domain", return_value=None)
    @mock.patch("updateHostsFile.gather_custom_exclusions", return_value=None)
    def test_mixture_gather_exclusions(self, mock_gather, mock_exclude, _):
        common_exclusions = ["foo", "bar"]
        display_exclusion_options(common_exclusions, "foo", [])

        mock_exclude.assert_called_once_with("foo", "foo", [])
        self.assert_called_once(mock_gather)


class TestGatherCustomExclusions(BaseStdout):

    # Can only test in the invalid domain case
    # because of the settings global variable.
    @mock.patch("updateHostsFile.raw_input", side_effect=["foo", "no"])
    @mock.patch("updateHostsFile.is_valid_domain_format", return_value=False)
    def test_basic(self, *_):
        gather_custom_exclusions("foo", [])

        expected = "Do you have more domains you want to enter? [Y/n]"
        output = sys.stdout.getvalue()
        self.assertIn(expected, output)

    @mock.patch("updateHostsFile.raw_input", side_effect=["foo", "yes",
                                                          "bar", "no"])
    @mock.patch("updateHostsFile.is_valid_domain_format", return_value=False)
    def test_multiple(self, *_):
        gather_custom_exclusions("foo", [])

        expected = ("Do you have more domains you want to enter? [Y/n] "
                    "Do you have more domains you want to enter? [Y/n]")
        output = sys.stdout.getvalue()
        self.assertIn(expected, output)


class TestExcludeDomain(Base):

    def test_invalid_exclude_domain(self):
        exclusion_regexes = []
        exclusion_pattern = "*.com"

        for domain in ["google.com", "hulu.com", "adaway.org"]:
            self.assertRaises(re.error, exclude_domain, domain,
                              exclusion_pattern, exclusion_regexes)

        self.assertListEqual(exclusion_regexes, [])

    def test_valid_exclude_domain(self):
        exp_count = 0
        expected_regexes = []
        exclusion_regexes = []
        exclusion_pattern = "[a-z]\."

        for domain in ["google.com", "hulu.com", "adaway.org"]:
            self.assertEqual(len(exclusion_regexes), exp_count)

            exclusion_regexes = exclude_domain(domain, exclusion_pattern,
                                               exclusion_regexes)
            expected_regex = re.compile(exclusion_pattern + domain)

            expected_regexes.append(expected_regex)
            exp_count += 1

        self.assertEqual(len(exclusion_regexes), exp_count)
        self.assertListEqual(exclusion_regexes, expected_regexes)


class TestMatchesExclusions(Base):

    def test_no_match_empty_list(self):
        exclusion_regexes = []

        for domain in ["1.2.3.4 localhost", "5.6.7.8 hulu.com",
                       "9.1.2.3 yahoo.com", "4.5.6.7 cloudfront.net"]:
            self.assertFalse(matches_exclusions(domain, exclusion_regexes))

    def test_no_match_list(self):
        exclusion_regexes = [".*\.org", ".*\.edu"]
        exclusion_regexes = [re.compile(regex) for regex in exclusion_regexes]

        for domain in ["1.2.3.4 localhost", "5.6.7.8 hulu.com",
                       "9.1.2.3 yahoo.com", "4.5.6.7 cloudfront.net"]:
            self.assertFalse(matches_exclusions(domain, exclusion_regexes))

    def test_match_list(self):
        exclusion_regexes = [".*\.com", ".*\.org", ".*\.edu"]
        exclusion_regexes = [re.compile(regex) for regex in exclusion_regexes]

        for domain in ["5.6.7.8 hulu.com", "9.1.2.3 yahoo.com",
                       "4.5.6.7 adaway.org", "8.9.1.2 education.edu"]:
            self.assertTrue(matches_exclusions(domain, exclusion_regexes))
# End Exclusion Logic


# Update Logic
class TestUpdateAllSources(BaseStdout):

    def setUp(self):
        BaseStdout.setUp(self)

        self.source_data_filename = "data.json"
        self.host_filename = "hosts.txt"

    @mock.patch(builtins() + ".open")
    @mock.patch("updateHostsFile.recursive_glob", return_value=[])
    def test_no_sources(self, _, mock_open):
        update_all_sources(self.source_data_filename, self.host_filename)
        mock_open.assert_not_called()

    @mock.patch(builtins() + ".open", return_value=mock.Mock())
    @mock.patch("json.load", return_value={"url": "example.com"})
    @mock.patch("updateHostsFile.recursive_glob", return_value=["foo"])
    @mock.patch("updateHostsFile.write_data", return_value=0)
    @mock.patch("updateHostsFile.get_file_by_url", return_value="file_data")
    def test_one_source(self, mock_get, mock_write, *_):
        update_all_sources(self.source_data_filename, self.host_filename)
        self.assert_called_once(mock_write)
        self.assert_called_once(mock_get)

        output = sys.stdout.getvalue()
        expected = "Updating source  from example.com"

        self.assertIn(expected, output)

    @mock.patch(builtins() + ".open", return_value=mock.Mock())
    @mock.patch("json.load", return_value={"url": "example.com"})
    @mock.patch("updateHostsFile.recursive_glob", return_value=["foo"])
    @mock.patch("updateHostsFile.write_data", return_value=0)
    @mock.patch("updateHostsFile.get_file_by_url",
                return_value=Exception("fail"))
    def test_source_fail(self, mock_get, mock_write, *_):
        update_all_sources(self.source_data_filename, self.host_filename)
        mock_write.assert_not_called()
        self.assert_called_once(mock_get)

        output = sys.stdout.getvalue()
        expecteds = ["Updating source  from example.com",
                     "Error in updating source:  example.com"]
        for expected in expecteds:
            self.assertIn(expected, output)

    @mock.patch(builtins() + ".open", return_value=mock.Mock())
    @mock.patch("json.load", side_effect=[{"url": "example.com"},
                                          {"url": "example2.com"}])
    @mock.patch("updateHostsFile.recursive_glob", return_value=["foo", "bar"])
    @mock.patch("updateHostsFile.write_data", return_value=0)
    @mock.patch("updateHostsFile.get_file_by_url",
                side_effect=[Exception("fail"), "file_data"])
    def test_sources_fail_succeed(self, mock_get, mock_write, *_):
        update_all_sources(self.source_data_filename, self.host_filename)
        self.assert_called_once(mock_write)

        get_calls = [mock.call("example.com"), mock.call("example2.com")]
        mock_get.assert_has_calls(get_calls)

        output = sys.stdout.getvalue()
        expecteds = ["Updating source  from example.com",
                     "Error in updating source:  example.com",
                     "Updating source  from example2.com"]
        for expected in expecteds:
            self.assertIn(expected, output)
# End Update Logic


# File Logic
class TestNormalizeRule(BaseStdout):

    def test_no_match(self):
        kwargs = dict(target_ip="0.0.0.0", keep_domain_comments=False)

        for rule in ["foo", "128.0.0.1", "bar.com/usa", "0.0.0 google",
                     "0.0.0.0 1.2.34.34", "0.1.2.3.4 foo/bar", "twitter.com"]:
            self.assertEqual(normalize_rule(rule, **kwargs), (None, None))

            output = sys.stdout.getvalue()
            sys.stdout = StringIO()

            expected = "==>" + rule + "<=="
            self.assertIn(expected, output)

    def test_no_comments(self):
        for target_ip in ("0.0.0.0", "127.0.0.1", "8.8.8.8"):
            rule = "127.0.0.1 1.google.com foo"
            expected = ("1.google.com", str(target_ip) + " 1.google.com\n")

            actual = normalize_rule(rule, target_ip=target_ip,
                                    keep_domain_comments=False)
            self.assertEqual(actual, expected)

            # Nothing gets printed if there's a match.
            output = sys.stdout.getvalue()
            self.assertEqual(output, "")

            sys.stdout = StringIO()

    def test_with_comments(self):
        for target_ip in ("0.0.0.0", "127.0.0.1", "8.8.8.8"):
            for comment in ("foo", "bar", "baz"):
                rule = "127.0.0.1 1.google.co.uk " + comment
                expected = ("1.google.co.uk",
                            (str(target_ip) + " 1.google.co.uk # " +
                             comment + "\n"))

                actual = normalize_rule(rule, target_ip=target_ip,
                                        keep_domain_comments=True)
                self.assertEqual(actual, expected)

                # Nothing gets printed if there's a match.
                output = sys.stdout.getvalue()
                self.assertEqual(output, "")

                sys.stdout = StringIO()


class TestStripRule(Base):

    def test_strip_empty(self):
        for line in ["0.0.0.0", "domain.com", "foo"]:
            output = strip_rule(line)
            self.assertEqual(output, "")

    def test_strip_exactly_two(self):
        for line in ["0.0.0.0 twitter.com", "127.0.0.1 facebook.com",
                     "8.8.8.8 google.com", "1.2.3.4 foo.bar.edu"]:
            output = strip_rule(line)
            self.assertEqual(output, line)

    def test_strip_more_than_two(self):
        for line in ["0.0.0.0 twitter.com", "127.0.0.1 facebook.com",
                     "8.8.8.8 google.com", "1.2.3.4 foo.bar.edu"]:
            output = strip_rule(line + " # comments here galore")
            self.assertEqual(output, line)


class TestWriteOpeningHeader(BaseMockDir):

    def setUp(self):
        super(TestWriteOpeningHeader, self).setUp()
        self.final_file = BytesIO()

    def test_missing_keyword(self):
        kwargs = dict(extensions="", outputsubfolder="",
                      numberofrules=5, skipstatichosts=False)

        for k in kwargs.keys():
            bad_kwargs = kwargs.copy()
            bad_kwargs.pop(k)

            self.assertRaises(KeyError, write_opening_header,
                              self.final_file, **bad_kwargs)

    def test_basic(self):
        kwargs = dict(extensions="", outputsubfolder="",
                      numberofrules=5, skipstatichosts=True)
        write_opening_header(self.final_file, **kwargs)

        contents = self.final_file.getvalue()
        contents = contents.decode("UTF-8")

        # Expected contents.
        for expected in (
            "# This hosts file is a merged collection",
            "# with a dash of crowd sourcing via Github",
            "# Number of unique domains: {count}".format(
                count=kwargs["numberofrules"]),
            "Fetch the latest version of this file:",
            "Project home page: https://github.com/StevenBlack/hosts",
        ):
            self.assertIn(expected, contents)

        # Expected non-contents.
        for expected in (
            "# Extensions added to this file:",
            "127.0.0.1 localhost",
            "127.0.0.1 local",
            "127.0.0.53",
            "127.0.1.1",
        ):
            self.assertNotIn(expected, contents)

    def test_basic_include_static_hosts(self):
        kwargs = dict(extensions="", outputsubfolder="",
                      numberofrules=5, skipstatichosts=False)
        with self.mock_property("platform.system") as obj:
            obj.return_value = "Windows"
            write_opening_header(self.final_file, **kwargs)

        contents = self.final_file.getvalue()
        contents = contents.decode("UTF-8")

        # Expected contents.
        for expected in (
            "127.0.0.1 local",
            "127.0.0.1 localhost",
            "# This hosts file is a merged collection",
            "# with a dash of crowd sourcing via Github",
            "# Number of unique domains: {count}".format(
                count=kwargs["numberofrules"]),
            "Fetch the latest version of this file:",
            "Project home page: https://github.com/StevenBlack/hosts",
        ):
            self.assertIn(expected, contents)

        # Expected non-contents.
        for expected in (
            "# Extensions added to this file:",
            "127.0.0.53",
            "127.0.1.1",
        ):
            self.assertNotIn(expected, contents)

    def test_basic_include_static_hosts_linux(self):
        kwargs = dict(extensions="", outputsubfolder="",
                      numberofrules=5, skipstatichosts=False)
        with self.mock_property("platform.system") as system:
            system.return_value = "Linux"

            with self.mock_property("socket.gethostname") as hostname:
                hostname.return_value = "steven-hosts"
                write_opening_header(self.final_file, **kwargs)

        contents = self.final_file.getvalue()
        contents = contents.decode("UTF-8")

        # Expected contents.
        for expected in (
            "127.0.1.1",
            "127.0.0.53",
            "steven-hosts",
            "127.0.0.1 local",
            "127.0.0.1 localhost",
            "# This hosts file is a merged collection",
            "# with a dash of crowd sourcing via Github",
            "# Number of unique domains: {count}".format(
                count=kwargs["numberofrules"]),
            "Fetch the latest version of this file:",
            "Project home page: https://github.com/StevenBlack/hosts",
        ):
            self.assertIn(expected, contents)

        # Expected non-contents.
        expected = "# Extensions added to this file:"
        self.assertNotIn(expected, contents)

    def test_extensions(self):
        kwargs = dict(extensions=["epsilon", "gamma", "mu", "phi"],
                      outputsubfolder="", numberofrules=5,
                      skipstatichosts=True)
        write_opening_header(self.final_file, **kwargs)

        contents = self.final_file.getvalue()
        contents = contents.decode("UTF-8")

        # Expected contents.
        for expected in (
            ", ".join(kwargs["extensions"]),
            "# Extensions added to this file:",
            "# This hosts file is a merged collection",
            "# with a dash of crowd sourcing via Github",
            "# Number of unique domains: {count}".format(
                count=kwargs["numberofrules"]),
            "Fetch the latest version of this file:",
            "Project home page: https://github.com/StevenBlack/hosts",
        ):
            self.assertIn(expected, contents)

        # Expected non-contents.
        for expected in (
            "127.0.0.1 localhost",
            "127.0.0.1 local",
            "127.0.0.53",
            "127.0.1.1",
        ):
            self.assertNotIn(expected, contents)

    def test_no_preamble(self):
        # We should not even attempt to read this, as it is a directory.
        hosts_dir = os.path.join(self.test_dir, "myhosts")
        os.mkdir(hosts_dir)

        kwargs = dict(extensions="", outputsubfolder="",
                      numberofrules=5, skipstatichosts=True)

        with self.mock_property("updateHostsFile.BASEDIR_PATH"):
            updateHostsFile.BASEDIR_PATH = self.test_dir
            write_opening_header(self.final_file, **kwargs)

        contents = self.final_file.getvalue()
        contents = contents.decode("UTF-8")

        # Expected contents.
        for expected in (
            "# This hosts file is a merged collection",
            "# with a dash of crowd sourcing via Github",
            "# Number of unique domains: {count}".format(
                count=kwargs["numberofrules"]),
            "Fetch the latest version of this file:",
            "Project home page: https://github.com/StevenBlack/hosts",
        ):
            self.assertIn(expected, contents)

        # Expected non-contents.
        for expected in (
            "# Extensions added to this file:",
            "127.0.0.1 localhost",
            "127.0.0.1 local",
            "127.0.0.53",
            "127.0.1.1",
        ):
            self.assertNotIn(expected, contents)

    def test_preamble(self):
        hosts_file = os.path.join(self.test_dir, "myhosts")
        with open(hosts_file, "w") as f:
            f.write("peter-piper-picked-a-pepper")

        kwargs = dict(extensions="", outputsubfolder="",
                      numberofrules=5, skipstatichosts=True)

        with self.mock_property("updateHostsFile.BASEDIR_PATH"):
            updateHostsFile.BASEDIR_PATH = self.test_dir
            write_opening_header(self.final_file, **kwargs)

        contents = self.final_file.getvalue()
        contents = contents.decode("UTF-8")

        # Expected contents.
        for expected in (
            "peter-piper-picked-a-pepper",
            "# This hosts file is a merged collection",
            "# with a dash of crowd sourcing via Github",
            "# Number of unique domains: {count}".format(
                count=kwargs["numberofrules"]),
            "Fetch the latest version of this file:",
            "Project home page: https://github.com/StevenBlack/hosts",
        ):
            self.assertIn(expected, contents)

        # Expected non-contents.
        for expected in (
            "# Extensions added to this file:",
            "127.0.0.1 localhost",
            "127.0.0.1 local",
            "127.0.0.53",
            "127.0.1.1",
        ):
            self.assertNotIn(expected, contents)

    def tearDown(self):
        super(TestWriteOpeningHeader, self).tearDown()
        self.final_file.close()


class TestUpdateReadmeData(BaseMockDir):

    def setUp(self):
        super(TestUpdateReadmeData, self).setUp()
        self.readme_file = os.path.join(self.test_dir, "readmeData.json")

    def test_missing_keyword(self):
        kwargs = dict(extensions="", outputsubfolder="",
                      numberofrules="", sourcesdata="")

        for k in kwargs.keys():
            bad_kwargs = kwargs.copy()
            bad_kwargs.pop(k)

            self.assertRaises(KeyError, update_readme_data,
                              self.readme_file, **bad_kwargs)

    def test_add_fields(self):
        with open(self.readme_file, "w") as f:
            json.dump({"foo": "bar"}, f)

        kwargs = dict(extensions=None, outputsubfolder="foo",
                      numberofrules=5, sourcesdata="hosts")
        update_readme_data(self.readme_file, **kwargs)

        expected = {
            "base": {
                "location": "foo" + self.sep,
                "sourcesdata": "hosts",
                "entries": 5,
            },
            "foo": "bar"
        }

        with open(self.readme_file, "r") as f:
            actual = json.load(f)
            self.assertEqual(actual, expected)

    def test_modify_fields(self):
        with open(self.readme_file, "w") as f:
            json.dump({"base": "soprano"}, f)

        kwargs = dict(extensions=None, outputsubfolder="foo",
                      numberofrules=5, sourcesdata="hosts")
        update_readme_data(self.readme_file, **kwargs)

        expected = {
            "base": {
                "location": "foo" + self.sep,
                "sourcesdata": "hosts",
                "entries": 5,
            }
        }

        with open(self.readme_file, "r") as f:
            actual = json.load(f)
            self.assertEqual(actual, expected)

    def test_set_extensions(self):
        with open(self.readme_file, "w") as f:
            json.dump({}, f)

        kwargs = dict(extensions=["com", "org"], outputsubfolder="foo",
                      numberofrules=5, sourcesdata="hosts")
        update_readme_data(self.readme_file, **kwargs)

        expected = {
            "com-org": {
                "location": "foo" + self.sep,
                "sourcesdata": "hosts",
                "entries": 5,
            }
        }

        with open(self.readme_file, "r") as f:
            actual = json.load(f)
            self.assertEqual(actual, expected)


class TestMoveHostsFile(BaseStdout):

    @mock.patch("os.path.abspath", side_effect=lambda f: f)
    def test_move_hosts_no_name(self, _):
        with self.mock_property("os.name"):
            os.name = "foo"

            mock_file = mock.Mock(name="foo")
            move_hosts_file_into_place(mock_file)

            expected = ""
            output = sys.stdout.getvalue()

            self.assertEqual(output, expected)

    @mock.patch("os.path.abspath", side_effect=lambda f: f)
    def test_move_hosts_windows(self, _):
        with self.mock_property("os.name"):
            os.name = "nt"

            mock_file = mock.Mock(name="foo")
            move_hosts_file_into_place(mock_file)

            expected = ("Automatically moving the hosts "
                        "file in place is not yet supported.\n"
                        "Please move the generated file to "
                        "%SystemRoot%\system32\drivers\etc\hosts")
            output = sys.stdout.getvalue()
            self.assertIn(expected, output)

    @mock.patch("os.path.abspath", side_effect=lambda f: f)
    @mock.patch("subprocess.call", return_value=0)
    def test_move_hosts_posix(self, *_):
        with self.mock_property("os.name"):
            os.name = "posix"

            mock_file = mock.Mock(name="foo")
            move_hosts_file_into_place(mock_file)

            expected = ("Moving the file requires administrative "
                        "privileges. You might need to enter your password.")
            output = sys.stdout.getvalue()
            self.assertIn(expected, output)

    @mock.patch("os.path.abspath", side_effect=lambda f: f)
    @mock.patch("subprocess.call", return_value=1)
    def test_move_hosts_posix_fail(self, *_):
        with self.mock_property("os.name"):
            os.name = "posix"

            mock_file = mock.Mock(name="foo")
            move_hosts_file_into_place(mock_file)

            expected = "Moving the file failed."
            output = sys.stdout.getvalue()
            self.assertIn(expected, output)


class TestFlushDnsCache(BaseStdout):

    @mock.patch("subprocess.call", return_value=0)
    def test_flush_darwin(self, _):
        with self.mock_property("platform.system") as obj:
            obj.return_value = "Darwin"
            flush_dns_cache()

            expected = ("Flushing the DNS cache to utilize new hosts "
                        "file...\nFlushing the DNS cache requires "
                        "administrative privileges. You might need to "
                        "enter your password.")
            output = sys.stdout.getvalue()
            self.assertIn(expected, output)

    @mock.patch("subprocess.call", return_value=1)
    def test_flush_darwin_fail(self, _):
        with self.mock_property("platform.system") as obj:
            obj.return_value = "Darwin"
            flush_dns_cache()

            expected = "Flushing the DNS cache failed."
            output = sys.stdout.getvalue()
            self.assertIn(expected, output)

    def test_flush_windows(self):
        with self.mock_property("platform.system") as obj:
            obj.return_value = "win32"

            with self.mock_property("os.name"):
                os.name = "nt"
                flush_dns_cache()

                expected = ("Automatically flushing the DNS cache is "
                            "not yet supported.\nPlease copy and paste "
                            "the command 'ipconfig /flushdns' in "
                            "administrator command prompt after running "
                            "this script.")
                output = sys.stdout.getvalue()
                self.assertIn(expected, output)

    @mock.patch("os.path.isfile", return_value=False)
    def test_flush_no_tool(self, _):
        with self.mock_property("platform.system") as obj:
            obj.return_value = "Linux"

            with self.mock_property("os.name"):
                os.name = "posix"
                flush_dns_cache()

                expected = "Unable to determine DNS management tool."
                output = sys.stdout.getvalue()
                self.assertIn(expected, output)

    @mock.patch("os.path.isfile", side_effect=[True] + [False] * 10)
    @mock.patch("subprocess.call", return_value=0)
    def test_flush_posix(self, *_):
        with self.mock_property("platform.system") as obj:
            obj.return_value = "Linux"

            with self.mock_property("os.name"):
                os.name = "posix"
                flush_dns_cache()

                expected = ("Flushing the DNS cache by "
                            "restarting nscd succeeded")
                output = sys.stdout.getvalue()
                self.assertIn(expected, output)

    @mock.patch("os.path.isfile", side_effect=[True] + [False] * 10)
    @mock.patch("subprocess.call", return_value=1)
    def test_flush_posix_fail(self, *_):
        with self.mock_property("platform.system") as obj:
            obj.return_value = "Linux"

            with self.mock_property("os.name"):
                os.name = "posix"
                flush_dns_cache()

                expected = ("Flushing the DNS cache by "
                            "restarting nscd failed")
                output = sys.stdout.getvalue()
                self.assertIn(expected, output)

    @mock.patch("os.path.isfile", side_effect=[True, False,
                                               True] + [False] * 10)
    @mock.patch("subprocess.call", side_effect=[1, 0])
    def test_flush_posix_fail_then_succeed(self, *_):
        with self.mock_property("platform.system") as obj:
            obj.return_value = "Linux"

            with self.mock_property("os.name"):
                os.name = "posix"
                flush_dns_cache()

                output = sys.stdout.getvalue()
                for expected in [("Flushing the DNS cache by "
                                  "restarting nscd failed"),
                                 ("Flushing the DNS cache by restarting "
                                  "NetworkManager.service succeeded")]:
                    self.assertIn(expected, output)


def mock_path_join_robust(*args):
    # We want to hard-code the backup hosts filename
    # instead of parametrizing based on current time.
    if len(args) == 2 and args[1].startswith("hosts-"):
        return os.path.join(args[0], "hosts-new")
    else:
        return os.path.join(*args)


class TestRemoveOldHostsFile(BaseMockDir):

    def setUp(self):
        super(TestRemoveOldHostsFile, self).setUp()
        self.hosts_file = os.path.join(self.test_dir, "hosts")

    def test_remove_hosts_file(self):
        old_dir_count = self.dir_count

        with self.mock_property("updateHostsFile.BASEDIR_PATH"):
            updateHostsFile.BASEDIR_PATH = self.test_dir
            remove_old_hosts_file(backup=False)

            new_dir_count = old_dir_count + 1
            self.assertEqual(self.dir_count, new_dir_count)

            with open(self.hosts_file, "r") as f:
                contents = f.read()
                self.assertEqual(contents, "")

    def test_remove_hosts_file_exists(self):
        with open(self.hosts_file, "w") as f:
            f.write("foo")

        old_dir_count = self.dir_count

        with self.mock_property("updateHostsFile.BASEDIR_PATH"):
            updateHostsFile.BASEDIR_PATH = self.test_dir
            remove_old_hosts_file(backup=False)

            new_dir_count = old_dir_count
            self.assertEqual(self.dir_count, new_dir_count)

            with open(self.hosts_file, "r") as f:
                contents = f.read()
                self.assertEqual(contents, "")

    @mock.patch("updateHostsFile.path_join_robust",
                side_effect=mock_path_join_robust)
    def test_remove_hosts_file_backup(self, _):
        with open(self.hosts_file, "w") as f:
            f.write("foo")

        old_dir_count = self.dir_count

        with self.mock_property("updateHostsFile.BASEDIR_PATH"):
            updateHostsFile.BASEDIR_PATH = self.test_dir
            remove_old_hosts_file(backup=True)

            new_dir_count = old_dir_count + 1
            self.assertEqual(self.dir_count, new_dir_count)

            with open(self.hosts_file, "r") as f:
                contents = f.read()
                self.assertEqual(contents, "")

            new_hosts_file = self.hosts_file + "-new"

            with open(new_hosts_file, "r") as f:
                contents = f.read()
                self.assertEqual(contents, "foo")
# End File Logic


# Helper Functions
def mock_url_open(url):
    """
    Mock of `urlopen` that returns the url in a `BytesIO` stream.

    Parameters
    ----------
    url : str
        The URL associated with the file to open.

    Returns
    -------
    bytes_stream : BytesIO
        The `url` input wrapped in a `BytesIO` stream.
    """

    return BytesIO(url)


def mock_url_open_fail(_):
    """
    Mock of `urlopen` that fails with an Exception.
    """

    raise Exception()


def mock_url_open_read_fail(_):
    """
    Mock of `urlopen` that returns an object that fails on `read`.

    Returns
    -------
    file_mock : mock.Mock
        A mock of a file object that fails when reading.
    """

    def fail_read():
        raise Exception()

    m = mock.Mock()

    m.read = fail_read
    return m


def mock_url_open_decode_fail(_):
    """
    Mock of `urlopen` that returns an object that fails on during decoding
    the output of `urlopen`.

    Returns
    -------
    file_mock : mock.Mock
        A mock of a file object that fails when decoding the output.
    """

    def fail_decode(_):
        raise Exception()

    def read():
        s = mock.Mock()
        s.decode = fail_decode

        return s

    m = mock.Mock()
    m.read = read
    return m


class GetFileByUrl(BaseStdout):

    @mock.patch("updateHostsFile.urlopen",
                side_effect=mock_url_open)
    def test_read_url(self, _):
        url = b"www.google.com"

        expected = "www.google.com"
        actual = get_file_by_url(url)

        self.assertEqual(actual, expected)

    @mock.patch("updateHostsFile.urlopen",
                side_effect=mock_url_open_fail)
    def test_read_url_fail(self, _):
        url = b"www.google.com"
        self.assertIsNone(get_file_by_url(url))

        expected = "Problem getting file:"
        output = sys.stdout.getvalue()

        self.assertIn(expected, output)

    @mock.patch("updateHostsFile.urlopen",
                side_effect=mock_url_open_read_fail)
    def test_read_url_read_fail(self, _):
        url = b"www.google.com"
        self.assertIsNone(get_file_by_url(url))

        expected = "Problem getting file:"
        output = sys.stdout.getvalue()

        self.assertIn(expected, output)

    @mock.patch("updateHostsFile.urlopen",
                side_effect=mock_url_open_decode_fail)
    def test_read_url_decode_fail(self, _):
        url = b"www.google.com"
        self.assertIsNone(get_file_by_url(url))

        expected = "Problem getting file:"
        output = sys.stdout.getvalue()

        self.assertIn(expected, output)


class TestWriteData(Base):

    def test_write_basic(self):
        f = BytesIO()

        data = "foo"
        write_data(f, data)

        expected = b"foo"
        actual = f.getvalue()

        self.assertEqual(actual, expected)

    def test_write_unicode(self):
        f = BytesIO()

        data = u"foo"
        write_data(f, data)

        expected = b"foo"
        actual = f.getvalue()

        self.assertEqual(actual, expected)


class TestQueryYesOrNo(BaseStdout):

    def test_invalid_default(self):
        for invalid_default in ["foo", "bar", "baz", 1, 2, 3]:
            self.assertRaises(ValueError, query_yes_no, "?", invalid_default)

    @mock.patch("updateHostsFile.raw_input", side_effect=["yes"] * 3)
    def test_valid_default(self, _):
        for valid_default, expected in [(None, "[y/n]"), ("yes", "[Y/n]"),
                                        ("no", "[y/N]")]:
            self.assertTrue(query_yes_no("?", valid_default))

            output = sys.stdout.getvalue()
            sys.stdout = StringIO()

            self.assertIn(expected, output)

    @mock.patch("updateHostsFile.raw_input", side_effect=([""] * 2))
    def test_use_valid_default(self, _):
        for valid_default in ["yes", "no"]:
            expected = (valid_default == "yes")
            actual = query_yes_no("?", valid_default)

            self.assertEqual(actual, expected)

    @mock.patch("updateHostsFile.raw_input", side_effect=["no", "NO", "N",
                                                          "n", "No", "nO"])
    def test_valid_no(self, _):
        self.assertFalse(query_yes_no("?", None))

    @mock.patch("updateHostsFile.raw_input", side_effect=["yes", "YES", "Y",
                                                          "yeS", "y", "YeS",
                                                          "yES", "YEs"])
    def test_valid_yes(self, _):
        self.assertTrue(query_yes_no("?", None))

    @mock.patch("updateHostsFile.raw_input", side_effect=["foo", "yes",
                                                          "foo", "no"])
    def test_invalid_then_valid(self, _):
        expected = "Please respond with 'yes' or 'no'"

        # The first time, we respond "yes"
        self.assertTrue(query_yes_no("?", None))

        output = sys.stdout.getvalue()
        self.assertIn(expected, output)

        sys.stdout = StringIO()

        # The second time, we respond "no"
        self.assertFalse(query_yes_no("?", None))

        output = sys.stdout.getvalue()
        self.assertIn(expected, output)


class TestIsValidDomainFormat(BaseStdout):

    def test_empty_domain(self):
        self.assertFalse(is_valid_domain_format(""))

        output = sys.stdout.getvalue()
        expected = "You didn't enter a domain. Try again."

        self.assertTrue(expected in output)

    def test_invalid_domain(self):
        expected = ("Do not include www.domain.com or "
                    "http(s)://domain.com. Try again.")

        for invalid_domain in ["www.subdomain.domain", "https://github.com",
                               "http://www.google.com"]:
            self.assertFalse(is_valid_domain_format(invalid_domain))

            output = sys.stdout.getvalue()
            sys.stdout = StringIO()

            self.assertIn(expected, output)

    def test_valid_domain(self):
        for valid_domain in ["github.com", "travis.org", "twitter.com"]:
            self.assertTrue(is_valid_domain_format(valid_domain))

            output = sys.stdout.getvalue()
            sys.stdout = StringIO()

            self.assertEqual(output, "")


def mock_walk(stem):
    """
    Mock method for `os.walk`.

    Please refer to the documentation of `os.walk` for information about
    the provided parameters.
    """

    files = ["foo.txt", "bar.bat", "baz.py", "foo/foo.c", "foo/bar.doc",
             "foo/baz/foo.py", "bar/foo/baz.c", "bar/bar/foo.bat"]

    if stem == ".":
        stem = ""

    matches = []

    for f in files:
        if not stem or f.startswith(stem + "/"):
            matches.append(("", "_", [f]))

    return matches


class TestRecursiveGlob(Base):

    @staticmethod
    def sorted_recursive_glob(stem, file_pattern):
        actual = recursive_glob(stem, file_pattern)
        actual.sort()

        return actual

    @mock.patch("os.walk", side_effect=mock_walk)
    def test_all_match(self, _):
        with self.mock_property("sys.version_info"):
            sys.version_info = (2, 6)

            expected = ["bar.bat", "bar/bar/foo.bat",
                        "bar/foo/baz.c", "baz.py",
                        "foo.txt", "foo/bar.doc",
                        "foo/baz/foo.py", "foo/foo.c"]
            actual = self.sorted_recursive_glob("*", "*")
            self.assertListEqual(actual, expected)

            expected = ["bar/bar/foo.bat", "bar/foo/baz.c"]
            actual = self.sorted_recursive_glob("bar", "*")
            self.assertListEqual(actual, expected)

            expected = ["foo/bar.doc", "foo/baz/foo.py", "foo/foo.c"]
            actual = self.sorted_recursive_glob("foo", "*")
            self.assertListEqual(actual, expected)

    @mock.patch("os.walk", side_effect=mock_walk)
    def test_file_ending(self, _):
        with self.mock_property("sys.version_info"):
            sys.version_info = (2, 6)

            expected = ["foo/baz/foo.py"]
            actual = self.sorted_recursive_glob("foo", "*.py")
            self.assertListEqual(actual, expected)

            expected = ["bar/foo/baz.c", "foo/foo.c"]
            actual = self.sorted_recursive_glob("*", "*.c")
            self.assertListEqual(actual, expected)

            expected = []
            actual = self.sorted_recursive_glob("*", ".xlsx")
            self.assertListEqual(actual, expected)


def mock_path_join(*_):
    """
    Mock method for `os.path.join`.

    Please refer to the documentation of `os.path.join` for information about
    the provided parameters.
    """

    raise UnicodeDecodeError("foo", b"", 1, 5, "foo")


class TestPathJoinRobust(Base):

    def test_basic(self):
        expected = "path1"
        actual = path_join_robust("path1")
        self.assertEqual(actual, expected)

        actual = path_join_robust(u"path1")
        self.assertEqual(actual, expected)

    def test_join(self):
        for i in range(1, 4):
            paths = ["pathNew"] * i
            expected = "path1" + (self.sep + "pathNew") * i
            actual = path_join_robust("path1", *paths)

            self.assertEqual(actual, expected)

    def test_join_unicode(self):
        for i in range(1, 4):
            paths = [u"pathNew"] * i
            expected = "path1" + (self.sep + "pathNew") * i
            actual = path_join_robust("path1", *paths)

            self.assertEqual(actual, expected)

    @mock.patch("os.path.join", side_effect=mock_path_join)
    def test_join_error(self, _):
        self.assertRaises(locale.Error, path_join_robust, "path")


# Colors
class TestSupportsColor(BaseStdout):

    def test_posix(self):
        with self.mock_property("sys.platform"):
            sys.platform = "Linux"

            with self.mock_property("sys.stdout.isatty") as obj:
                obj.return_value = True
                self.assertTrue(supports_color())

    def test_pocket_pc(self):
        with self.mock_property("sys.platform"):
            sys.platform = "Pocket PC"
            self.assertFalse(supports_color())

    def test_windows_no_ansicon(self):
        with self.mock_property("sys.platform"):
            sys.platform = "win32"

            with self.mock_property("os.environ"):
                os.environ = []

                self.assertFalse(supports_color())

    def test_windows_ansicon(self):
        with self.mock_property("sys.platform"):
            sys.platform = "win32"

            with self.mock_property("os.environ"):
                os.environ = ["ANSICON"]

                with self.mock_property("sys.stdout.isatty") as obj:
                    obj.return_value = True
                    self.assertTrue(supports_color())

    def test_no_isatty_attribute(self):
        with self.mock_property("sys.platform"):
            sys.platform = "Linux"

            with self.mock_property("sys.stdout"):
                sys.stdout = list()
                self.assertFalse(supports_color())

    def test_no_isatty(self):
        with self.mock_property("sys.platform"):
            sys.platform = "Linux"

            with self.mock_property("sys.stdout.isatty") as obj:
                obj.return_value = False
                self.assertFalse(supports_color())


class TestColorize(Base):

    def setUp(self):
        self.text = "house"
        self.colors = ["red", "orange", "yellow",
                       "green", "blue", "purple"]

    @mock.patch("updateHostsFile.supports_color", return_value=False)
    def test_colorize_no_support(self, _):
        for color in self.colors:
            expected = self.text
            actual = colorize(self.text, color)

            self.assertEqual(actual, expected)

    @mock.patch("updateHostsFile.supports_color", return_value=True)
    def test_colorize_support(self, _):
        for color in self.colors:
            expected = color + self.text + Colors.ENDC
            actual = colorize(self.text, color)

            self.assertEqual(actual, expected)


class TestPrintSuccess(BaseStdout):

    def setUp(self):
        super(TestPrintSuccess, self).setUp()
        self.text = "house"

    @mock.patch("updateHostsFile.supports_color", return_value=False)
    def test_print_success_no_support(self, _):
        print_success(self.text)

        expected = self.text + "\n"
        actual = sys.stdout.getvalue()

        self.assertEqual(actual, expected)

    @mock.patch("updateHostsFile.supports_color", return_value=True)
    def test_print_success_support(self, _):
        print_success(self.text)

        expected = Colors.SUCCESS + self.text + Colors.ENDC + "\n"
        actual = sys.stdout.getvalue()

        self.assertEqual(actual, expected)


class TestPrintFailure(BaseStdout):

    def setUp(self):
        super(TestPrintFailure, self).setUp()
        self.text = "house"

    @mock.patch("updateHostsFile.supports_color", return_value=False)
    def test_print_failure_no_support(self, _):
        print_failure(self.text)

        expected = self.text + "\n"
        actual = sys.stdout.getvalue()

        self.assertEqual(actual, expected)

    @mock.patch("updateHostsFile.supports_color", return_value=True)
    def test_print_failure_support(self, _):
        print_failure(self.text)

        expected = Colors.FAIL + self.text + Colors.ENDC + "\n"
        actual = sys.stdout.getvalue()

        self.assertEqual(actual, expected)
# End Helper Functions


if __name__ == "__main__":
    unittest.main()
