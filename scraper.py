from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.firefox.options import Options
import sys
import time
import calendar
import utils
from settings import BROWSER_EXE, FIREFOX_BINARY, GECKODRIVER, PROFILE
from webdriver_manager.firefox import GeckoDriverManager
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException, StaleElementReferenceException

class CollectPosts(object):
    """Collector of recent FaceBook posts.
           Note: We bypass the FaceBook-Graph-API by using a 
           selenium FireFox instance! 
           This is against the FB guide lines and thus not allowed.

           USE THIS FOR EDUCATIONAL PURPOSES ONLY. DO NOT ACTAULLY RUN IT.
    """

    def __init__(self, ids=["oxfess"], file="posts_group.csv", depth=5, delay=2):
        self.ids = ids
        self.out_file = file
        self.depth = depth + 1
        self.delay = delay
        # browser instance
        self.browser = webdriver.Firefox(executable_path=GeckoDriverManager().install())
        # self.browser = webdriver.Firefox(executable_path=GECKODRIVER,
        #                                  firefox_binary=FIREFOX_BINARY,
        #                                  firefox_profile=PROFILE,)

        utils.create_csv(self.out_file)

    def collect_page(self, page):
        # navigate to page
        self.browser.get(
            'https://www.facebook.com/' + page + '/')

        # Scroll down depth-times and wait delay seconds to load
        # between scrolls
        for scroll in range(self.depth):

            # Scroll down to bottom
            self.browser.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);")

            # Wait to load page
            time.sleep(self.delay)

        # Once the full page is loaded, we can start scraping
        links = self.browser.find_elements_by_link_text("See more")

        for link in links:
            print("in for loop opening link")
            WebDriverWait(self.browser, 30).until(EC.element_to_be_clickable((By.LINK_TEXT,
                                                                          "See more")))
            link.click()
            print("opening link")
        posts = self.browser.find_elements_by_class_name(
            "userContentWrapper")

        for count, post in enumerate(posts):
            # Creating first CSV row entry with the poster name (eg. "Donald Trump")
            analysis = []
            time_element = post.find_element_by_css_selector("abbr")
            utime = time_element.get_attribute("data-utime")

            id_element = post.find_element_by_class_name("_232_")
            idpost = id_element.get_attribute("id")

            try:
                if int(str(idpost).split(";;")[-1]) == 9:
                    texts = str(idpost).split(";;")[0].split("feed_subtitle_")[1]
                    id_page = texts.split(";")[0]
                    id_post = texts.split(";")[1]
                    analysis.append(utime)
                    analysis.append(id_page)
                    analysis.append(id_post)
                    # Creating post text entry
                    text = post.find_element_by_class_name("userContent").text
                    status = utils.strip(text)
                    analysis.append(status)


                # Write row to csv
                utils.write_to_csv(self.out_file, analysis)
            except:pass

            # get comment
            ""
            tmp = post.find_element_by_class_name("commentable_item")
            out = []
            # click to open comments
            ele = tmp.find_element_by_class_name('_4vn2').find_element_by_class_name("_3hg-")
            ele.click()

            # 查看更多留言、查看更多回覆(view more comments)
            while True:
                try:
                    # wait for loading cycle icon to disappear
                    WebDriverWait(tmp, 8).until_not(
                        EC.presence_of_element_located((By.CSS_SELECTOR, '.mls.img._55ym._55yn._55yo'))
                    )
                    pager = WebDriverWait(tmp, 8).until(
                        EC.visibility_of_element_located((By.CLASS_NAME, 'UFIPagerLink'))
                    )
                    pager.click()
                except StaleElementReferenceException:
                    print('element not attached to the page')
                except TimeoutException:
                    print('done "view more comments"')
                    break
            try:
                tmp.find_element_by_class_name("_3hg").click()
                print("da click")
            except:pass

            tmp2 = tmp.find_element_by_class_name("_7a8-")
            print("da tim thay 7a9a")
            cmmts = tmp2.find_element_by_class_name("_42ef")
            print("da tim thay 42ef")
            print(cmmts)
            input()

            for counts, cmm in enumerate(cmmts):
                textcm = cmm.find_element_by_class_name("_3l3x").text
                out.append(utils.strip(textcm))

            print(out)
            input()


    def collect_groups(self, group):
        # navigate to page
        self.browser.get(
            'https://www.facebook.com/groups/' + group + '/')

        # Scroll down depth-times and wait delay seconds to load
        # between scrolls
        for scroll in range(self.depth):

            # Scroll down to bottom
            self.browser.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);")

            # Wait to load page
            time.sleep(self.delay)

        # Once the full page is loaded, we can start scraping
        links = self.browser.find_elements_by_link_text("See more")

        for link in links:
            print("in for loop opening link")
            WebDriverWait(self.browser, 30).until(EC.element_to_be_clickable((By.LINK_TEXT,
                                                                              "See more")))
            link.click()
            print("opening link")
        input()
        posts = self.browser.find_elements_by_class_name(
            "sjgh65i0")

        for count, post in enumerate(posts):
            # Creating first CSV row entry with the poster name (eg. "Donald Trump")
            print(post)
            input()
            analysis = []
            time_element = post.find_element_by_css_selector("abbr")
            utime = time_element.get_attribute("data-utime")

            id_element = post.find_element_by_class_name("_232_")
            idpost = id_element.get_attribute("id")
            try:
                if int(str(idpost).split(";;")[-1]) == 9:
                    texts = str(idpost).split(";;")[0].split("feed_subtitle_")[1]
                    id_page = texts.split(";")[0]
                    id_post = texts.split(";")[1]
                    analysis.append(utime)
                    analysis.append(id_page)
                    analysis.append(id_post)
                    # Creating post text entry
                    text = post.find_element_by_class_name("c1et5uql").text
                    status = utils.strip(text)
                    analysis.append(status)
                # Write row to csv
                utils.write_to_csv(self.out_file, analysis)
            except:
                pass

    def collect(self, typ):
        if typ == "groups":
            for iden in self.ids:
                self.collect_groups(iden)
        elif typ == "pages":
            for iden in self.ids:
                self.collect_page(iden)
        self.browser.close()

    def safe_find_element_by_id(self, elem_id):
        try:
            return self.browser.find_element_by_id(elem_id)
        except NoSuchElementException:
            return None

    def login(self, email, password):
        try:

            self.browser.get("https://www.facebook.com")
            self.browser.maximize_window()

            # filling the form
            self.browser.find_element_by_name('email').send_keys(email)
            self.browser.find_element_by_name('pass').send_keys(password)

            # clicking on login button
            self.browser.find_element_by_id('loginbutton').click()
            # if your account uses multi factor authentication
            mfa_code_input = self.safe_find_element_by_id('approvals_code')

            if mfa_code_input is None:
                return

            mfa_code_input.send_keys(input("Enter MFA code: "))
            self.browser.find_element_by_id('checkpointSubmitButton').click()

            # there are so many screens asking you to verify things. Just skip them all
            while self.safe_find_element_by_id('checkpointSubmitButton') is not None:
                dont_save_browser_radio = self.safe_find_element_by_id('u_0_3')
                if dont_save_browser_radio is not None:
                    dont_save_browser_radio.click()

                self.browser.find_element_by_id(
                    'checkpointSubmitButton').click()

        except Exception as e:
            print("There was some error while logging in.")
            print(sys.exc_info()[0])
            exit()

'''_5f4c
_5pcp _5lel _2jyu _232_'''