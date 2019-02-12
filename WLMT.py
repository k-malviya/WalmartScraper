from bs4 import BeautifulSoup
from array import *
import requests
import sys
import math
import urllib.request
import platform
import urllib
import csv
qryparam = ''
for arg in sys.argv:
    qryparam = qryparam + '%20' + arg
qryparam = qryparam[13:]
print(qryparam)
# print(sys.argv)

baseReqStr = 'https://www.walmart.com/search/?cat_id=0&query=' + qryparam
hdr = {'User-Agent': 'Mozilla/5.0', "content-type": "text"}
print('URL', baseReqStr)
response = requests.get(baseReqStr)
text = BeautifulSoup(response.text, 'html.parser')
text.find_all({'class': "product-title-link line-clamp line-clamp-2"})

# Get total number of products
num_products = text.find('div', {'class': "result-summary-container"})
print(num_products)
strNumProd = ''.join(num_products)

NumOfProducts = int(strNumProd[8:-8].replace(',', ''))
print ("Products to parse = ", NumOfProducts)
NumOfPages = math.ceil(NumOfProducts/20)
print ("Pages to parse = ", NumOfPages)
ProdLastPage = NumOfPages*20 - NumOfProducts
if ProdLastPage == 0:
    ProdLastPage = 20
print (ProdLastPage)
# Now built the URL list to parse through
pages = []
PageL = 'https://www.walmart.com/search/?page='
PageR = '&query=' + qryparam + '#searchProductResult'
for i in range(NumOfPages):
    j = i+1
    pages.insert(i, PageL+str(j)+PageR)
    #print(i, PageL+str(j)+PageR)

headers = requests.utils.default_headers()
default_agent = headers['User-Agent']

headers.update(
    {
        'User-Agent': default_agent + ' (' + platform.platform() + ')',
    }
)

csvFileName = qryparam.replace('%20', ' ')+'.csv'
with open(csvFileName, 'w', encoding='utf-8') as csvFile:
    walmartWriter = csv.writer(csvFile)
# Parse through the URLs and fetch products
    pageNum = 1
    for pageURL in pages:
        print(pageURL)
        dic = {}
        responsePage = requests.get(pageURL, headers=headers)
        pageText = BeautifulSoup(responsePage.text, 'lxml')
        # search-result-listview-item Grid
        prodToParseThisPage = len(pageText.findAll(
            'a', {'class': "product-title-link line-clamp line-clamp-2"}))
        #print('prodToParseThisPage ', prodToParseThisPage)

        # Start fetching products for that page

        for cntr in range(prodToParseThisPage):
            pageRank = cntr+1

            try:
                cls = 'ProductTileListView-'+str(cntr)
                prodName = pageText.find("div", {"data-tl-id": cls}).find(
                    'a', {'class': "product-title-link line-clamp line-clamp-2"}).get('aria-label')
                prodURL = pageText.find("div", {"data-tl-id": cls}).find(
                    'a', {'class': "product-title-link line-clamp line-clamp-2"}).get('href')
                prodURLLen = len(prodURL)
                sponsoredProduct = False  # Is this a sponsored product
                # Product ID on Walmart.com
                prodId = prodURL[prodURLLen - 8:]
                # Resolve the issue with Sponsored URLs
                if prodId == '_aduid__':
                    prodId = prodURL[:prodURLLen - 205]
                    length1 = len(prodId)
                    prodId = prodId[length1 - 8:]
                    sponsoredProduct = True
                # print(prodId)
                # print(sponsoredProduct)
                sellPrice = pageText.find("div", {"data-tl-id": cls}).find(
                    'span', {'class': "price display-inline-block arrange-fit price price-main"})
                if sellPrice is None:
                    sellPrice = 'Not Available'
                else:
                    sellPrice = pageText.find("div", {"data-tl-id": cls}).find(
                        'span', {'class': "price display-inline-block arrange-fit price price-main"}).get_text()

                ListPrice = pageText.find("div", {"data-tl-id": cls}).find(
                    'span', {'class': "product-list-price-block listview"})  # .find('span', {'class': "price-group"}).get('aria-label')
                # print(sellPrice)
                if ListPrice is None:
                    # print(ListPrice)
                    ListPrice = 'Not available'
                else:
                    #print('else loop')
                    ListPrice = pageText.find("div", {"data-tl-id": cls}).find(
                        'span', {'class': "product-list-price-block listview"}).find('span', {'class': "price-group"}).get('aria-label')
                    # print(ListPrice)

                freeShip = pageText.find("div", {"data-tl-id": cls}).find(
                    'div', {'class': "ShippingMessage-container color-green font-bold"})

                if freeShip is None:
                    freeShip = 'Not Available'
                else:
                    freeShip = "Available"
                # print(freeShip)
                AveRatingBlock = pageText.find("div", {"data-tl-id": cls}).find(
                    'span', {'class': "seo-avg-rating"})
                # print(AveRating)
                if AveRatingBlock is None:
                    AveRating = 'Not Available'
                else:
                    AveRating = pageText.find("div", {"data-tl-id": cls}).find(
                        'span', {'class': "seo-avg-rating"}).get_text()
                # print(AveRating)
                # stars-reviews-count
                countRatingBlock = pageText.find("div", {"data-tl-id": cls}).find(
                    'span', {'class': "stars-reviews-count"})
                if countRatingBlock is None:
                    reviewCount = 'Not Available'
                else:
                    reviewCount = pageText.find("div", {"data-tl-id": cls}).find(
                        'span', {'class': "stars-reviews-count"}).get_text()[:-7]
                # print(reviewCount)

                brandBlock = pageText.find("div", {"data-tl-id": cls}).find(
                    'div', {'class': "see-all-link"})
                if brandBlock is None:
                    brandName = 'Not Available'
                else:
                    brandName = pageText.find("div", {"data-tl-id": cls}).find(
                        'div', {'class': "see-all-link"}).get_text().replace("Show only ", "").replace(" items", "")
                # print(brandName)

                sellerBlock = pageText.find("div", {"data-tl-id": cls}).find(
                    'span', {'class': "marketplace-sold-by-company-name"})
                if sellerBlock is None:
                    sellerName = 'Walmart'
                else:
                    sellerName = pageText.find("div", {"data-tl-id": cls}).find(
                        'span', {'class': "marketplace-sold-by-company-name"}).get_text()
                # print(sellerName)

                # Set these in dictionary now
                dic['prodName'] = prodName
                dic['prodId'] = prodId
                dic['sponsoredProduct'] = sponsoredProduct
                dic['sellPrice'] = sellPrice
                dic['ListPrice'] = ListPrice
                dic['freeShip'] = freeShip
                dic['AveRating'] = AveRating
                dic['reviewCount'] = reviewCount
                dic['brandName'] = brandName
                dic['sellerName'] = sellerName
                dic['pageNum'] = pageNum
                dic['pageRank'] = pageRank
                dic['prodURL'] = prodURL
                walmartWriter.writerow(dic.values())

            except:
                print('skipped row ', pageRank, 'on page ', pageNum)

        pageNum = pageNum+1
