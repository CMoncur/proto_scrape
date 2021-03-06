""" ICODrops Excavator """

# Core Dependencies
from datetime import datetime

# External Dependencies
from bs4 import BeautifulSoup

# Internal Dependencies
from cryptkeeper.quarry.excavator import Excavator
from cryptkeeper.db.librarian import Librarian
import cryptkeeper.db.schema.icodrops as Schema
import cryptkeeper.util.util as Util


# Sanitization Functions
def containsAllData(entry):
  """ Ensures ICODrops entry contains all data needed to be stored """
  return isinstance(entry["name"], str) \
    and isinstance(entry["start"], datetime) \
    and isinstance(entry["end"], datetime) \
    and isinstance(entry["description"], str) \
    and isinstance(entry["price"], float) \
    and isinstance(entry["raised"], int) \
    and isinstance(entry["presale_start"], datetime) \
    and isinstance(entry["presale_end"], datetime) \
    and isinstance(entry["token_symbol"], str)


# Scraping Functions
def scrapeDescription(soup):
  """ Scrapes ICO description from ICODrops listing """
  return soup \
    .find("div", attrs = { "class" : "ico-main-info" }) \
    .text \
    .replace("\n", " ") \
    .translate({ ord(x): "" for x in ["\r", "\t" ] }) \
    .strip() \
    .split("  ", 1)[-1]


def scrapeEnd(soup):
  """ Scrapes ICO end date from ICODrops listing """
  year = str(datetime.now().year)
  token_sale = list(filter(lambda x: "Sale:" in x.text, soup.findAll("h4")))

  if token_sale:
    date_string = token_sale[0] \
      .text \
      .translate({ ord(x): "" for x in [ "\n", "\r", "\t" ] }) \
      .replace("Token Sale: ", "") \
      .split(" – ")[0]

    try:
      return datetime.strptime(date_string + " " + year, "%d %b %Y")

    except ValueError:
      # Return nothing in event string is still not formatted properly
      return None

  # Catchall in the event this entity was not scraped
  return None


def scrapeName(soup):
  """ Scrapes ICO name from ICODrops listing """
  return soup \
    .find("div", attrs = { "class" : "ico-main-info" }) \
    .find("h3").text


def scrapePrice(soup):
  """ Scrapes ICO price from ICODrops listing """
  li = soup.findAll("li")

  for idx, yeah in enumerate(li):
    span = yeah.find("span", attrs = { "class" : "grey" })

    if span and "Token Price" in span.text:
      price = li[idx] \
        .text \
        .split(" = ")[-1] \
        .split(" (")[0] \
        .replace("\xa0", " ") \
        .split(" ")[0]

      # Return only first match
      try:
        return float(price)

      except ValueError:
        # Return nothing in the event type casting fails
        return None

  # Catchall in the event no matches are found
  return None


def scrapeRaised(soup):
  """ Scrapes ICO amount raised from ICODrops listing """
  raised = soup \
    .find("div", attrs = { "class" : "money-goal" }) \
    .text \
    .translate({ ord(x): "" for x in [ "$", ",", "\n", "\r", "\t" ] })

  try:
    return int(raised)

  except ValueError:
    # Return nothing in the event type casting fails
    return None



def scrapeSite(soup):
  """ Scrapes ICO website URL from ICODrops listing """
  return soup \
    .find("div", attrs = { "class" : "ico-right-col" }) \
    .find("a")["href"]


def scrapeStart(soup):
  """ Scrapes ICO start date from ICODrops listing """
  year = str(datetime.now().year)
  token_sale = list(filter(lambda x: "Sale:" in x.text, soup.findAll("h4")))

  if token_sale:
    date_string = token_sale[0] \
      .text \
      .translate({ ord(x): "" for x in [ "\n", "\r", "\t" ] }) \
      .replace("Token Sale: ", "") \
      .split(" – ")[0]

    try:
      return datetime.strptime(date_string + " " + year, "%d %b %Y")

    except ValueError:
      # Return nothing in event string is still not formatted properly
      return None

  # Catchall in the event this entity was not scraped
  return None


def scrapeSymbol(soup):
  """ Scrapes ICO symbol from ICODrops listing """
  li = soup.findAll("li")

  for idx, yeah in enumerate(li):
    span = yeah.find("span", attrs = { "class" : "grey" })

    if span and "Ticker:" in span.text:
      # Return only first match
      return li[idx] \
        .text \
        .replace("Ticker: ", "")

  return None


# Public Entities
class IcoDrops(Excavator, Librarian):
  """ ICODrops Excavator Class """

  URL = "https://icodrops.com"

  def __init__(self):
    Excavator.__init__(self, self.__fetchIcoUrls(), True, True)
    Librarian.__init__(self, Schema.IcoDrops)
    self.raw_ico_data = []
    self.sanitized_ico_data = []

    if not self.urls:
      print("IcoDrops: No URLs to mine...")

    else:
      self.__fetchIcoData()
      self.__sanitizeAndStoreIcoData()


  # Private Methods
  def __fetchIcoData(self):
    """ Fetch metadata specific to each ICO """
    # Filter out non-HTML responses
    self.data = list(filter(Util.isHtml, self.data))

    for data in self.data:
      soup = BeautifulSoup(data["content"], "html.parser")

      self.raw_ico_data.append({
        "name" : scrapeName(soup),
        "start" : scrapeStart(soup),
        "end" : scrapeEnd(soup),
        "description" : scrapeDescription(soup),
        "price" : scrapePrice(soup),
        "raised" : scrapeRaised(soup),
        "presale_start" : scrapeStart(soup),
        "presale_end" : scrapeEnd(soup),
        "token_symbol" : scrapeSymbol(soup)
      })


  def __fetchIcoUrls(self):
    """
    Within IcoDrops, there are three main columns -- 1) Active ICO,
    2) Upcoming ICO, 3) Ended ICO. Each column has a "View All" anchor at
    the bottom of the list.  This function will grab the URLs for each of
    those "View All" links and append them to a list.

    Utilizing each of the gathered ICO List URLs, fetch the URLS of each
    individual ICO, and append them to a list.
    """
    icodrops_home = Excavator([ self.URL ], True, True)
    ico_list_urls = []
    ico_urls = []

    if Util.isHtml(icodrops_home.data[0]):
      soup = BeautifulSoup(icodrops_home.data[0]["content"], "html.parser")

      for s in soup.findAll("div", attrs = { "id" : "view_all" }):
        ico_list_urls.append(self.URL + s.find("a")["href"])

    ico_lists = Excavator(ico_list_urls, True, True)

    for data in ico_lists.data:
      if Util.isHtml(data):
        soup = BeautifulSoup(data["content"], "html.parser")

        for a in soup.findAll("a", attrs = { "id" : "ccc" }):
          ico_urls.append(a["href"])

    return ico_urls


  def __sanitizeAndStoreIcoData(self):
    """
    Ensures only values with all essential information are included, then
    upserts data to Postgres.
    """
    self.sanitized_ico_data = list(filter(containsAllData, self.raw_ico_data))

    # Inherited from Librarian class
    self.bulkUpsert(
      self.sanitized_ico_data,
      [ Schema.IcoDrops.name.name ]
    )
