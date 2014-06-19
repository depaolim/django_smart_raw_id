import unittest

from django.contrib.auth.models import User
from django.test import LiveServerTestCase, TestCase

from selenium.webdriver.firefox.webdriver import WebDriver

from .models import *


LABEL_URL = "/admin/test_app/singlesale/label_view/test_app/product/"


class TestLabelViewUrl(TestCase):

    def test_reverse_raw_id_label(self):
        from django.core.urlresolvers import reverse
        self.assertEqual(
            reverse("admin:test_app_singlesale_raw_id_label", args=('test_app', 'product')),
            LABEL_URL)

    def test_reverse_raw_id_multi_label(self):
        from django.core.urlresolvers import reverse
        self.assertEqual(
            reverse("admin:test_app_stocksale_raw_id_multi_label", args=('test_app', 'product')),
            "/admin/test_app/stocksale/label_view/test_app/product/multi/")


class TestViews(TestCase):

    def setUp(self):
        super(TestViews, self).setUp()
        PASSWORD = "my_password"
        self.bread, _created = Product.objects.get_or_create(name='bread')
        self.flour, _created = Product.objects.get_or_create(name='flour')
        self.u = User.objects.create_user(username='my_name', password=PASSWORD)
        self.u.is_staff = True
        self.u.save()
        self.client.login(username=self.u.username, password=PASSWORD)

    def test_get_label_view(self):
        response = self.client.get(LABEL_URL, {"pk": self.bread.pk})
        self.assertContains(response, "bread")

    def test_get_singlesale_view(self):
        self.u.is_superuser = True
        self.u.save()
        response = self.client.get("/admin/test_app/singlesale/add/")
        self.assertContains(response, "bread")


class TestAcceptance(LiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        import os
        try:
            del os.environ['http_proxy']
        except KeyError:
            pass
        cls.browser = WebDriver()
        cls.browser.implicitly_wait(20)
        super(TestAcceptance, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        cls.browser.quit()
        super(TestAcceptance, cls).tearDownClass()

    def setUp(self):
        super(TestAcceptance, self).setUp()
        Product.objects.get_or_create(name='bread')
        Product.objects.get_or_create(name='flour')
        self.milk, _created = Product.objects.get_or_create(name='milk')
        self.spam, _created = Product.objects.get_or_create(name='spam')
        u = User.objects.create_user(username='my_name', password="my_password")
        u.is_staff = True
        u.is_superuser = True
        u.save()
        self.get_page()
        self.browser.find_element_by_name("username").send_keys("my_name")
        self.browser.find_element_by_name("password").send_keys("my_password")
        self.browser.find_element_by_xpath('//input[@value="Log in"]').click()
        self.browser.implicitly_wait(20)

    def tearDown(self):
        self.browser.find_element_by_xpath('//a[@href="/admin/logout/"]').click()
        self.browser.implicitly_wait(20)
        super(TestAcceptance, self).tearDown()

    def get_page(self, url=""):
        self.browser.implicitly_wait(20)
        self.browser.get("{}/admin/{}".format(self.live_server_url, url))

    @unittest.skip("keyboard input is not available")
    def test_single_sale_add_keyboard_input(self):
        self.get_page("test_app/singlesale/add/")
        self.browser.find_element_by_name("product").send_keys(str(self.spam.pk))
        self.browser.find_element_by_name("price").send_keys("10")
        self.browser.find_element_by_xpath('//input[@value="Save"]').click()
        self.assertItemsEqual([(u'spam', 10),], SingleSale.objects.values_list('product__name', 'price'))

    @unittest.skip("keyboard input is not available")
    def test_stock_sale_add_keyboard_input(self):
        self.get_page("test_app/stocksale/add/")
        self.browser.find_element_by_name("products").send_keys("{},{}".format(str(self.spam.pk), str(self.milk.pk)))
        self.browser.find_element_by_name("price").send_keys("50")
        self.browser.find_element_by_xpath('//input[@value="Save"]').click()
        self.assertItemsEqual(
            [(self.milk.pk, 50), (self.spam.pk, 50),],
            StockSale.objects.values_list('products', 'price'))

    def _select_product_from_popup_window(self, lookup_id_product, product_name):
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.support.ui import WebDriverWait

        self.browser.find_element_by_id(lookup_id_product).click()
        main_window_handle = self.browser.current_window_handle
        window_handles = self.browser.window_handles
        window_handles.remove(main_window_handle)
        self.browser.switch_to.window(window_handles[0])
        wait = WebDriverWait(self.browser, 10)
        wait.until(EC.element_to_be_clickable((By.TAG_NAME, 'a')))
        self.browser.find_element_by_xpath("//a[contains(text(),'{}')]".format(product_name)).click()
        self.browser.switch_to.window(main_window_handle)

    def test_single_sale_add_selection_input(self):
        self.get_page("test_app/singlesale/add/")
        self._select_product_from_popup_window("lookup_id_product", "spam")
        self.browser.find_element_by_name("price").send_keys("10")
        self.browser.find_element_by_xpath('//input[@value="Save"]').click()
        self.assertItemsEqual([(u'spam', 10),], SingleSale.objects.values_list('product__name', 'price'))

    def test_single_sale_change_selection_input(self):
        ss = SingleSale.objects.create(product=self.milk, price=23)
        self.get_page("test_app/singlesale/{}".format(ss.pk))
        self._select_product_from_popup_window("lookup_id_product", "spam")
        self.assertTrue(self.browser.find_element_by_xpath("//a[contains(text(),'{}')]".format("spam")))
        e_price = self.browser.find_element_by_name("price")
        e_price.clear()
        e_price.send_keys("10")
        self.browser.find_element_by_xpath('//input[@value="Save"]').click()
        self.assertItemsEqual([(u'spam', 10),], SingleSale.objects.values_list('product__name', 'price'))

    def test_stock_sale_add_selection_input(self):
        self.get_page("test_app/stocksale/add/")
        self._select_product_from_popup_window("lookup_id_products", "milk")
        self._select_product_from_popup_window("lookup_id_products", "spam")
        self.assertTrue(self.browser.find_element_by_xpath("//a[contains(text(),'{}')]".format("spam")))
        self.browser.find_element_by_name("price").send_keys("50")
        self.browser.find_element_by_xpath('//input[@value="Save"]').click()
        self.assertItemsEqual(
            [(self.milk.pk, 50), (self.spam.pk, 50),],
            StockSale.objects.values_list('products', 'price'))

