from django.test import TestCase
from explorer.actions import generate_report_action
from explorer.tests.factories import SimpleQueryFactory
from explorer import app_settings
from explorer.utils import passes_blacklist, schema_info, param, swap_params


class TestSqlBlacklist(TestCase):

    def setUp(self):
        self.orig = app_settings.EXPLORER_SQL_BLACKLIST

    def tearDown(self):
        app_settings.EXPLORER_SQL_BLACKLIST = self.orig

    def test_overriding_blacklist(self):
        app_settings.EXPLORER_SQL_BLACKLIST = []
        r = SimpleQueryFactory(sql="SELECT 1+1 AS \"DELETE\";")
        fn = generate_report_action()
        result = fn(None, None, [r, ])
        self.assertEqual(result.content, 'DELETE\r\n2\r\n')

    def test_default_blacklist_prevents_deletes(self):
        r = SimpleQueryFactory(sql="SELECT 1+1 AS \"DELETE\";")
        fn = generate_report_action()
        result = fn(None, None, [r, ])
        self.assertEqual(result.content, '0')

    def test_queries_modifying_functions_are_ok(self):
        sql = "SELECT 1+1 AS TWO; drop view foo;"
        self.assertTrue(passes_blacklist(sql))

    def test_queries_deleting_stuff_are_not_ok(self):
        sql = "'distraction'; delete from table; SELECT 1+1 AS TWO; drop view foo;"
        self.assertFalse(passes_blacklist(sql))

    def test_queries_dropping_views_is_ok_and_not_case_sensitive(self):
        sql = "SELECT 1+1 AS TWO; drop ViEw foo;"
        self.assertTrue(passes_blacklist(sql))


class TestSchemaInfo(TestCase):

    def test_schema_info_returns_valid_data(self):
        res = schema_info()
        tables = [a[1] for a in res]
        self.assertIn('explorer_query', tables)

    def test_app_exclusion_list(self):
        app_settings.EXPLORER_SCHEMA_EXCLUDE_APPS = ('explorer',)
        res = schema_info()
        app_settings.EXPLORER_SCHEMA_EXCLUDE_APPS = ('',)
        tables = [a[1] for a in res]
        self.assertNotIn('explorer_query', tables)


class TestParams(TestCase):

    def test_swappable_params_are_built_correctly(self):
        orig = app_settings.EXPLORER_PARAM_TOKEN
        app_settings.EXPLORER_PARAM_TOKEN = '!!'
        self.assertEqual('!!foo!!', param('foo'))
        app_settings.EXPLORER_PARAM_TOKEN = orig

    def test_params_get_swapped(self):
        app_settings.EXPLORER_PARAM_TOKEN = '$$'
        sql = 'please swap $$this$$ and $$that$$'
        expected = 'please swap here and there'
        params = {'this': 'here', 'that': 'there'}
        got = swap_params(sql, params)
        self.assertEqual(got, expected)

    def test_empty_params_does_nothing(self):
        app_settings.EXPLORER_PARAM_TOKEN = '$$'
        sql = 'please swap $$this$$ and $$that$$'
        params = None
        got = swap_params(sql, params)
        self.assertEqual(got, sql)

    def test_non_string_param_gets_swapper(self):
        app_settings.EXPLORER_PARAM_TOKEN = '$$'
        sql = 'please swap $$this$$'
        expected = 'please swap 1'
        params = {'this': 1}
        got = swap_params(sql, params)
        self.assertEqual(got, expected)