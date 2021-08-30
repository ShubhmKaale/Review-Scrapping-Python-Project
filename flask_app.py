from flask import Flask, render_template, request,jsonify
# from flask_cors import CORS,cross_origin
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen
import pymongo


app = Flask(__name__) #initiliazing the flask with name app

@app.route('/', methods=['POST','GET']) # route with allowed method
def index():
    if request.method =='POST':
        searchString = request.form['content'].replace(" ","%")# taking search field entered in form
        try:
            dbConn = pymongo.MongoClient("mongodb://localhost:27017/")# opening connection to mongo
            db = dbConn['scrapperDB'] # connecting to the database called scrapperDB if DB is not there it will creats as DB

            #checking if the keyword is already there in db or not
            reviews = db[searchString].find({}) # searching for the name same as keyword
            if reviews.count()>0:#
                return render_template('results.html', reviews= reviews)

            else:
                #preapraing the url to search
                flipkart_url = "https://www.flipkart.com/search?q=" + searchString

                uClient = urlopen(flipkart_url)#Requeting the webppage from the internet
                flipkartPage = uClient.read() # reading the webpage
                uClient.close() # closing the connceting to webpage

                # using beautiful soap as bs
                flipkart_html = bs(flipkartPage, "html.parser")# parsing the webpage as HTML, holding the html data of webpage

                bigboxes= flipkart_html.findAll("div", {"class": "_2kHMtA"})# searching for appripriate tag from inspection page
                box = bigboxes[0]# taking iteration for demo
                productlink = "https://www.flipkart.com" + box.a['href']# extracting the actual product link.
                prodpage = requests.get(productlink)#getting the product page from server
                prod_html = bs(prodpage.text,"html.parser") #parsing the product page as html
                commentboxes = prod_html.find_all('div', {'class': "_16PBlm"}) #find the area of comments

                table = db[searchString]# creating a collection same as search string

                reviews =[] # creating a empty list to hold review

                for comment in commentboxes:
                    try:
                        name = comment.div.div.find_all('p',{'class',"_2sc7ZR _2V5EHH"})[0].text #name:ankit
                    except:
                        name: "No name"

                    try:
                        rating = comment.div.div.div.div.text

                    except:
                        rating = "no rating"

                    try:
                        commenthead = comment.div.div.div.p.text
                    except:
                        commenthead = "no comment head"

                    #Saving the details to dictonary
                    mydict = {"Product": searchString, "Name": name,"Rating":rating, "CommentHead": commenthead}

                    #inserting collection in table
                    x = table.insert_one(mydict)
                    reviews.append(mydict) # appending the comments to reviw
                return render_template("results.html", reviews=reviews) # showing reviews
        except:
            #return "somethig is wrong"
            return render_template("results.html")

    else:
        return  render_template('index.html')


if __name__ == "__main__":
    app.run(port=8000, debug=True)












