import urllib
import json
import os
import pandas as pd
from flask import Flask
from flask import request
from flask import make_response
from wapy.api import Wapy
# Open the coke dataset

db = pd.read_csv('coke_full_new_db.csv', encoding='utf-8')
# setup
wapy = Wapy('rh8s4vtrpup9unq99rgams8j')
# Flask app should start in global layout
app = Flask(__name__)

@app.route('/webhook', methods=['POST'])

def webhook():
    req = request.get_json(silent=True, force=True)
    res = ""
    op=req.get("queryResult").get('parameters').get('operation')
    if op == 'price'or op=='':
        res = price(req)
        res = json.dumps(res, indent=4)
    elif op == 'rating':
        res = rating(req)
        res = json.dumps(res, indent=4)
    elif op == 'review':
        res = review(req)
        res = json.dumps(res, indent=4)
    elif op == 'availability':
        res = available(req)
        res = json.dumps(res, indent=4)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r

def price(req):
    result = req.get("queryResult")
    parameters = result.get("parameters")
    product = parameters.get("product")
    litre = int(parameters.get("litre_val"))
    cans = int(parameters.get("pack_val"))
    # Checking the database with three values
    sample =  db[db['name'].str.contains(product)][db['quantity_l']==litre][db['pack']==cans]
    if len(sample)>0:
        sample = sample[0:1]
        df = sample['name']
        df1 = sample['salePrice']
        df2 = df.astype('category')
        df3 = df1.astype('category')
        speech = "The price is ${0} for {1}, {2} litre/{3} cans. ".format(str(df3[0]),str(product),str(litre),str(cans))
    # if the litre value or pack value exceeds than in the database, but product is present in db. Goes to below code
    elif product in list(db['name']) and (len(db[db['quantity_l']==litre][db['pack']==cans])==0):
        speech = "Sorry, {0} with ‘{1} litre’ quantity and ‘{2} cans’ pack is not available.".format(str(product),str(litre),str(cans))
    # If nothing matches, prints the below code
    else:
        speech = "Sorry, I couldn’t find matching product for your search. "
    return {
        "fulfillmentText": speech,
}
def rating(req):
    result = req.get("queryResult")
    parameters = result.get("parameters")
    product = parameters.get("product")
    litre = int(parameters.get("litre_val"))
    cans = int(parameters.get("pack_val"))
    sample =  db[db['name'].str.contains(product)][db['quantity_l']==litre][db['pack']==cans]
    if len(sample)>0:
        sample = sample[0:1]
        df = sample['customerRating']
        df1 = df.astype('category')
        df2 = sample['name']
        df3 = df2.astype('category')
        if df1.isnull().all():
            speech = "Sorry, the product is not rated yet. "
        else:
            speech = "Rating of {0} is given to {1}, {2} litre/{3} cans.".format(str(df1[0]),str(product),str(litre),str(cans))
    else :
        speech = "Sorry, I couldn’t find matching product for your search. "
    return {
        "fulfillmentText": speech,
}
def available(req):
    result = req.get("queryResult")
    parameters = result.get("parameters")
    product = parameters.get("product")
    litre = int(parameters.get("litre_val"))
    cans = int(parameters.get("pack_val"))
    sample =  db[db['name'].str.contains(product)][db['quantity_l']==litre][db['pack']==cans]
    if len(sample)>0:
        sample = sample[0:1]
        df = sample['stock']
        df1 = df.astype('category')
        df2 = sample['name']
        df3 = df2.astype('category')
        speech = "The Product {0} is {1} .".format(df3[0],str(df1[0]))
    else :
        speech = "Sorry, I couldn’t find matching product for your search. "
    return {
        "fulfillmentText": speech,
}
def review(req):
    result = req.get("queryResult")
    parameters = result.get("parameters")
    product = parameters.get("product")
    litre = int(parameters.get("litre_val"))
    cans = int(parameters.get("pack_val"))
    sample =  db[db['name'].str.contains(product)][db['quantity_l']==litre][db['pack']==cans]
    sample = sample[0:1]
    if len(sample) > 0:
        df = sample['review']
        df1 = df.astype('category')
        df2 = sample['name']
        df3 = df2.astype('category')
        #df4 = sample['numReviews']
        #df5 = df4.astype('category')
        if df1.isnull().all():
            speech = "Sorry, the product is not reviewed yet."
            #speech = "Sorry, the product " str(product) +" Quantity : " +str(litre) + " Pack : " +str(cans)+" is not reviewed yet."
        else:
            speech = "“{0}” says review of {1}, {2} litre/{3} cans.".format(str(df1[0]),str(product),str(litre),str(cans))
            #"Review for the product " + str(product) +" Quantity : " +str(litre) + " Pack : " +str(cans)+" is : " + str(df1[0])
    else :
        speech = "Sorry, I couldn’t find matching product for your search. "
    return {
        "fulfillmentText": speech,
}
if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print ("Starting app on port %d" % port)

    app.run(debug=True, port=port, host='0.0.0.0')
