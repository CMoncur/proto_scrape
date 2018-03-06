""" ICODrops Excavator """

# External Dependencies
from bs4 import BeautifulSoup

# Internal Dependencies
from cryptkeeper.quarry.excavator import Excavator
import cryptkeeper.util.util as Util


# Scraping Functions
def scrapeName(soup):
  """ Scrapes ICO name from ICODrops listing """
  main_info = soup.find("div", attrs = { "class" : "ico-main-info" })
  return main_info.find("h3").text


# Public Entities
class IcoDrops(Excavator):
  """ ICODrops Excavator Class """

  URL = "https://icodrops.com"

  def __init__(self):
    # TODO: Uncomment when ready for real deal
    # super(IcoDrops, self).__init__(self.__fetchIcoUrls())
    self.ico_data = []
    yeah = self.__fetchIcoUrls()
    super(IcoDrops, self).__init__([ yeah[0] ], True, True)

    if not self.urls:
      print("IcoDrops: No URLs to mine...")

    else:
      self.__fetchIcoData()


  # Private Methods
  def __fetchIcoData(self):
    # Filter out non-HTML responses
    self.data = list(filter(Util.isHtml, self.data))

    for data in self.data:
      soup = BeautifulSoup(data["content"], "html.parser")

      self.ico_data.append({
        "name" : scrapeName(soup)
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
