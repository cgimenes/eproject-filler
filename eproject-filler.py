from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import sys, json, datetime


class EProjectFiller():

    def __init__(self, login_data):
        self.driver = webdriver.PhantomJS()
        self.action = webdriver.ActionChains(self.driver)
        self.driver.set_window_size(1024, 768)

        self.login_data = login_data

    def set_up(self):
        self.driver.get("http://www.projectpro.com.br/eproject.aspx")
        self.login()
        self.driver.save_screenshot("logged_in.png")
        self.driver.get("http://www.projectpro.com.br/modulos/lancamentos/novo/entradassaidasgrid.aspx")
        self.driver.save_screenshot("time_sheet.png")

    def tear_down(self):
        self.driver.save_screenshot("tear_down.png")
        self.driver.close()

    def parse_str_date(self, date):
        return datetime.datetime.strptime(date, "%Y-%m-%d").date()

    def get_elements_id(self, day):
        field_prefix = "cph_CONTEUDO_radGridDados_ctl00_ctl%02d" % (day + 4)

        return {
            "row": "cph_CONTEUDO_radGridDados_ctl00__%d" % (day - 1),
            "history": "%s_imbHistorico" % field_prefix,
            "arrived": "%s_ctl03" % field_prefix,
            "first-int": "%s_ctl04" % field_prefix,
            "first-ret": "%s_ctl05" % field_prefix,
            "second-int": "%s_ctl06" % field_prefix,
            "second-ret": "%s_ctl07" % field_prefix,
            "left": "%s_ctl08" % field_prefix,
            "comments": "%s_ctl14" % field_prefix
        }

    def fill_element(self, element, text):
        elem = self.driver.find_element_by_id(element)
        elem.clear()
        elem.send_keys(text)

    def click_element(self, element):
        elem = self.driver.find_element_by_id(element)
        elem.click()

    def double_click_element(self, element):
        elem = self.driver.find_element_by_id(element)

        self.action.move_to_element(elem)
        self.action.click()
        self.action.send_keys("")
        self.action.double_click()
        self.action.perform()

    def login(self):
        self.fill_element("txtUsuario", self.login_data.get("username"))
        self.fill_element("txtsenha", self.login_data.get("password"))
        self.click_element("btnLogin")

    def has_element(self, element):
        try:
            self.driver.find_element_by_id(element)
            return True
        except NoSuchElementException:
            return False

    def wait_for_page_loader(self):
        block_ui_locator = (By.CSS_SELECTOR, ".blockUI.blockOverlay")
        WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located(block_ui_locator))
        WebDriverWait(self.driver, 10).until(EC.invisibility_of_element_located(block_ui_locator))

    def edit_row(self, row_element):
        self.double_click_element(row_element)
        self.wait_for_page_loader()
        self.driver.save_screenshot("edit_row.png")

    def fill_row(self, ids, day_data):
        self.fill_element(ids["arrived"], day_data["arrived"])
        self.fill_element(ids["first-int"], day_data["first-int"])
        self.fill_element(ids["first-ret"], day_data["first-ret"])
        self.fill_element(ids["second-int"], day_data["second-int"])
        self.fill_element(ids["second-ret"], day_data["second-ret"])
        self.fill_element(ids["left"], day_data["left"])
        self.fill_element(ids["comments"], day_data["comments"])
        self.driver.save_screenshot("fill_row.png")

    def save_row(self):
        self.click_element("cph_CONTEUDO_radGridDados_ctl00")
        self.wait_for_page_loader()
        self.driver.save_screenshot("save_row.png")

    def run(self, data):
        try:
            self.set_up()

            for day_data in data:
                parsed_date = self.parse_str_date(day_data["date"])
                ids = self.get_elements_id(parsed_date.day)

                if self.has_element(ids["history"]):
                    pass  # TODO: check for modifications
                else:
                    self.edit_row(ids["row"])
                    self.fill_row(ids, day_data)
                    self.save_row()

        finally:
            self.tear_down()


if __name__ == "__main__":
    filler = EProjectFiller({"username": sys.argv[1], "password": sys.argv[2]})

    with open(sys.argv[3]) as data_file:
        data = json.load(data_file)

    filler.run(data)
