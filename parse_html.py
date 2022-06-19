from bs4 import BeautifulSoup

class Merchant:
    def __init__(self, cols):
        self.name = cols[0].string
        self.region = cols[1].string
        self.zone = cols[2].find("a").string
        self.zone_img = cols[2].find("a")['href']
        self.card = cols[3].find(class_="item").string
        self.votes = int(cols[5].find(class_="votes").string)
    def tostring(self):
        return ", ".join([self.name, self.region, self.zone, self.zone_img, self.card, self.votes])

def iterateMerchants(html):
    # the features arg is system dependent! remove it when migrating to new system
    soup = BeautifulSoup(html, features="html.parser")
    table = soup.find("table")
    if table:
        rows = table.find_all("tr")
        for row in rows:
            if "Suggest Replacement" in str(row):
                values = row.find_all("td")
                yield Merchant(values)

if __name__ == "__main__":
    html = open("example_page.html", "r").read()
    for merchant in iterateMerchants(html):
        print(merchant.tostring())