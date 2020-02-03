import pandas as pd
import numpy as np
import re
from progressbar import ProgressBar
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options


class TwitchScrapping:
    def __init__(self):
        self.webdriver = "/Users/mac/Downloads/chromedriver"
        self.opt = Options()
        self.opt.add_argument('--headless')
        self.opt.add_argument('--window-size=1920,1080')

    @staticmethod
    def get_email(string_text):
        match = re.search(r'[\w\.-]+@[\w\.-]+(\.[\w]+)+', string_text)
        if match:
            return match.group(0)
        return ''

    def get_twitch_videos(self, user_name):
        driver = Chrome(self.webdriver, options=self.opt)
        driver.implicitly_wait(5)
        url = f'https://www.twitch.tv/{user_name}/videos'
        driver.get(url)
        tx = ''
        tx = driver.find_elements_by_class_name(
            "tw-pd-x-2")[0].find_element_by_tag_name('h2').text
        if not tx:
            tx = 0
        return tx

    def get_twitter_email(self, url):
        driver = Chrome(self.webdriver, options=self.opt)

        driver.get(url)
        email = ''
        try:
            el = driver.find_elements_by_class_name('ProfileHeaderCard-bio')
            email = self.get_email(el[0].text)
            driver.quit()
        except:
            driver.quit()
            pass
        return email

    def get_facebook_email(self, url):
        driver = Chrome(self.webdriver, options=self.opt)
        driver.get(url)
        email = ''
        try:
            el = driver.find_elements_by_id('content_container')
            email = self.get_email(el[0].text)
            driver.quit()
        except:
            pass
        driver.quit()
        return email

    def get_links_from_twitch(self, username):
        driver = Chrome(self.webdriver, options=self.opt)
        driver.implicitly_wait(5)

        url = f'https://www.twitch.tv/{username}'
        driver.get(url)
        links = []
        email = ''
        try:
            elements = driver.find_elements_by_css_selector(
                "div.default-panel a")
            try:
                about = driver.find_elements_by_class_name(
                    "channel-panels")[0].text
                email = self.get_email(about)
            except:
                pass
            for element in elements:
                links.append(element.get_attribute("href"))
            try:
                driver.find_element_by_xpath(
                    "//*[contains(text(), 'The broadcaster has indicated')]")
            except:
                pass
            driver.quit()
        except:
            pass
        return links, email

    def get_is_sport(self):
        driver = Chrome(self.webdriver, options=self.opt)
        driver.implicitly_wait(5)
        import time
        # start_time = time.time()
        url = f'https://www.twitch.tv/lamaaatv'
        driver.get(url)
        # driver.find_elements_by_class_name('tw-pd-x-2')[0]
        elements = driver.find_elements_by_class_name('tw-pd-x-2')[0]
        # print("--- %s seconds --- \n\n\n" % (time.time() - start_time))
        # print("--- %s seconds ---" % (time.time() - start_time))
        # start_time = time.time()
        # time.sleep(2)

        # elements = driver.find_elements_by_class_name('tw-pd-x-2')[0]
            # print(elements.text)
        # print(elements.text, '<<<<<<>>>>>> \n\n')
        # driver.quit()
        for i in range(3):
            print("\n\n\n\n\n\n >>>>>>>>>>>>>>>>> \n\n", elements.text)
        res = elements.text.lower()
        import pdb; pdb.set_trace()


class DataExtraction(TwitchScrapping):
    def __init__(self):
        super(DataExtraction, self).__init__()
        df = pd.read_excel(
            '/Users/mac/Downloads/streamer_profiles_page_56.xlsx')
        df = df.dropna(how='all')
        df['fb_link'] = np.nan
        df['youtube_link'] = np.nan
        df['ig_link'] = np.nan
        df['twitter_link'] = np.nan
        self.df = df.fillna('')

    def remove_uneccessary_links(self, df):
        df = self.df
        for i in range(0, len(df)):
            name = df.iloc[i:i+1, ]['display_name'].item()

            if df.loc[df['display_name'] == name, 'email'].item():
                df.loc[df['display_name'] == name, 'fb_link'] = ''
                df.loc[df['display_name'] == name, 'youtube_link'] = ''
                df.loc[df['display_name'] == name, 'ig_link'] = ''
        return df

    def get_social_links(self):
        df = self.df
        pbar = ProgressBar().start()
        for i in range(len(df)):
            total = len(df)
            pbar.update((i/total)*100)  # current step/total steps * 100
            pbar.finish()
            name = df.iloc[i:i+1, ]['display_name'].item()
            if not df.loc[df['display_name'] == name, 'email'].item():
                print(
                    f".........{i}.......Start Filling data for {name} ......................... \n\n")
                links, email = self.get_links_from_twitch(name)
                source = df.loc[df['display_name']
                                == name, 'source_url'].item()
                tw_source = ''
                fb_source = ''
                for link in links:
                    if email:
                        source = f'https://www.twitch.tv/{name}'
                    if 'twitter.com' in link:
                        df.loc[df['display_name'] ==
                               name, 'twitter_link'] = link
                        tw_em = self.get_twitter_email(link)
                        email = tw_em if tw_em else email
                        tw_source = link if tw_em else source
                    if 'instagram.com' in link:
                        df.loc[df['display_name'] == name, 'ig_link'] = link
                    if 'facebook.com' in link:
                        username = link.split('/')[-2]
                        link = f'https://www.facebook.com/pg/{username}/about/?ref=page_internal'
                        df.loc[df['display_name'] == name, 'fb_link'] = link
                        fb_em = self.get_facebook_email(
                            link) if not email else email
                        email = fb_em if fb_em else email
                        fb_source = link if fb_em else ''
                    if 'youtube.com' in link:
                        df.loc[df['display_name'] == name,
                               'youtube_link'] = link + '/about'
                    df.loc[df['display_name'] == name, 'email'] = email
                    df.loc[df['display_name'] == name,
                           'source_url'] = tw_source or fb_source or source
                if links:
                    df.loc[df['display_name'] == name,
                           'number_of_videos'] = self.get_twitch_videos(name)
                print(
                    f"................End Filling data for {name} ......................... \n\n")
        df = self.remove_uneccessary_links(df)
        return df

    def scrap_data(self):
        df = self.get_social_links()
        df = df.drop(['view_count', 'twitter_link', 'fb_link'], axis=1)
        df.to_excel("streamer_profiles_page_56_trial.xlsx", sheet_name="streamer_profiles_page_56_trial", engine='xlsxwriter')


if __name__ == '__main__':
    scrap = TwitchScrapping()
    scrap.get_is_sport()