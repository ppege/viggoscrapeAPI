"""API v2 scraper, about 3 times as efficient as API v1"""
from unicodedata import normalize # pylint: disable=no-name-in-module
from pyquery import PyQuery as pq
from requests.exceptions import SSLError
from requests.exceptions import ConnectionError
from requests.sessions import Session
import requests

class CredentialError(Exception):
    """Thrown when HTML contains 'page-login', which indicates a failed login attempt"""

class Viggoscrape:
    """The main class. Takes 4 arguments, and uses those to get assignment data from viggo"""
    def __init__(
        self,
        login_data=None,
        subdomain=None,
        date=None,
        group_by_assignment=True,
        throw_errors_as_assignments=False
    ):
        self.login_data = login_data
        self.subdomain = subdomain
        self.date_selected = date
        self.group_by_assignment = group_by_assignment
        self.throw_errors_as_assignments = throw_errors_as_assignments
        self.html = None    # this variable will store the result of _get_html()
        self.data = None    # this variable will store the result of _get_variables()

    def get_assignments(self):
        """The main function that starts the scraping process and returns the data once scraped"""
        try:
            self._get_html()
        except (requests.exceptions.SSLError, requests.exceptions.ConnectionError, CredentialError) as exception:
            if self.throw_errors_as_assignments:
                return [
                    {
                        "author": "",
                        "date": "",
                        "description": str(exception),
                        "subject": "Error",
                        "time": "",
                        "url": ""
                    }
                ]
            return {"errors": [str(exception)]}
        except Exception as exception:
            if self.throw_errors_as_assignments:
                return [
                    {
                        "author": "",
                        "date": "",
                        "description": "Unknown error. Please report this to the developer. In the meantime, check your credentials for typos.",
                        "subject": "Error",
                        "time": "",
                        "url": ""
                    }
                ]
            return {"errors": ["Unknown error"]}
        if self.html == "The service is unavailable.":
            if self.throw_errors_as_assignments:
                return [
                    {
                        "author": "",
                        "date": "",
                        "description": "The ViGGO service is currently down.",
                        "subject": "Error",
                        "time": "",
                        "url": ""
                    }
                ]
            return {"errors": ["Viggo is currently down"]}
        self._get_variables()
        return self._create_dictionary()

    def _get_html(self):
        keys = self._define_keys()
        with Session() as session:
            try:
                pq(
                    f'https://{self.subdomain}.viggo.dk/Basic/Account/Login',
                    keys,
                    method='post',
                    session=session
                )
            except requests.exceptions.SSLError as ssl_error:
                try:
                    session.get("https://viggo.dk")
                except requests.exceptions.SSLError:
                    raise SSLError("Viggo is currently down.") from ssl_error
                raise SSLError("Invalid subdomain") from ssl_error
            except requests.exceptions.ConnectionError as connection_error:
                raise ConnectionError("No internet access on host machine") from connection_error
            url = f'''
                https://{self.subdomain}.viggo.dk/Basic/HomeworkAndAssignment/?date={self.date_selected}
            '''
            self.html = pq(session.get(url).content)
            if "page-login" in self.html.html():
                raise CredentialError("Invalid credentials")

    def _define_keys(self):
        return {
            "UserName": self.login_data["username"],
            "Password": self.login_data["password"]
        }

    def _get_variables(self):
        data = {
            'description': [
                normalize('NFKC', i.text()) for i in self.html('.content').items()
            ],
            'author': [i.text() for i in self.html('.fix-height').items()],
            'time': [i.parent().text() for i in self.html('.o-flaticon-info').items()],
            'date': self._get_date()
        }

        data["url"], data["subject"] = self._get_modal_items()
        self.data = data
        self._adjust_variables(self._get_item_count())
        self.data["errors"] = None

    def _get_item_count(self):

        var_list = self.data.values()
        return round(sum(len(list) for list in var_list)/len(var_list))

    def _adjust_variables(self, item_count):

        for _, value in self.data.items():
            list_length = len(value)
            if list_length <= item_count:
                for _ in range(item_count - list_length):
                    value.append(None)
            elif list_length >= item_count:
                for _ in range(list_length - item_count):
                    value.pop()

    def _get_date(self):

        items = self.html('.flaticon-homework').items()
        date = [pq(i.parent().parent().parent().children()[0]).text() for i in items]
        return list(date[1:])

    def _get_modal_items(self):

        modal = list(self.html('.ajaxModal').items())
        modal = [modal[i] for i in range(5, len(modal))]
        url = [f"https://{self.subdomain}.viggo.dk{i.attr('href')}" for i in modal]
        subject = [pq(item.html())("strong").text() for item in modal]

        return url, subject

    def _create_dictionary(self):

        return [
            {
                "description": self.data["description"][i],
                "subject": self.data["subject"][i],
                "author": self.data["author"][i],
                "date": self.data["date"][i],
                "time": self.data["time"][i],
                "url": self.data["url"][i]
            } for i, _ in enumerate(self.data["subject"])
        ] if self.group_by_assignment else self.data
