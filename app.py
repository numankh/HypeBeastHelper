from flask import Flask, request, jsonify, send_from_directory
import os
import psycopg2

"""
Basic app setup
"""
app = Flask(__name__, static_folder='frontend/build')

# Serve React App
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path != "" and os.path.exists(app.static_folder + '/' + path):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')

"""
Routes for PostgresQL database
"""

def config():
    try:
        conn = psycopg2.connect(
            host=os.getenv("PSQL_HOST"),
            database=os.getenv("PSQL_DATABASE"),
            user=os.getenv("PSQL_USER"),
            password=os.getenv("PSQL_PASSWORD"),
            port=os.getenv("PSQL_PORT"))

        return conn
    except Exception as e:
        print(str(e))
        return None

"""
CREATE APIs
"""
@app.route("/add_seller", methods=['POST'])
def add_seller():
    conn = None
    seller_id = None
    payload = {
        "username": request.form.get("username"),
        "positive": request.form.get("positive"),
        "neutral": request.form.get("neutral"),
        "negative": request.form.get("negative"),
        "join_date": request.form.get("join_date"),
        "followers": request.form.get("followers"),
        "positive_feedback": request.form.get("positive_feedback")
    }

    try:
        # Connect to psql db
        params = config()
        conn = psycopg2.connect(**params)
        cur = conn.cursor()

        # Execute insert statement
        seller_insert_sql_query = f"""INSERT INTO seller(username, positive, neutral, negative, join_date, followers, positive_feedback)
            VALUES('{payload["username"]}', {payload["positive"]}, {payload["neutral"]}, {payload["negative"]},
                    '{payload["join_date"]}', '{payload["followers"]}', {payload["positive_feedback"]}) RETURNING seller_id;"""
        cur.execute(seller_insert_sql_query)
        print("SUCCESS: Created SELLER record")
        seller_id = cur.fetchone()[0]

        # Close connection
        conn.commit()
        cur.close()
    except Exception as e:
        return(str(e))
    finally:
        if conn is not None:
            conn.close()

    return jsonify(f"Created seller record for seller <{payload['username']}> with seller_id <{seller_id}>")


@app.route("/add_shoe_listing", methods=['POST'])
def shoe_listing_herokudb(seller_id):
    payload = {
        "title": request.form.get("title"),
        "price": request.form.get("price"),
        "free_shipping": request.form.get("free_shipping"),
        "images": request.form.get("images"),
        "url": request.form.get("url"),
        "model": request.form.get("model"),
        "sold": request.form.get("sold"),
        "sold_date": request.form.get("sold_date"),
        "fre_score": request.form.get("fre_score"),
        "avg_grade_score": request.form.get("avg_grade_score"),
        "shoe_size": request.form.get("shoe_size"),
        "adult_shoe": request.form.get("adult_shoe"),
        "youth_shoe": request.form.get("youth_shoe"),
        "child_shoe": request.form.get("child_shoe")
    }
    

    try:
        conn = None
        listing_id = None
        params = config()
        conn = psycopg2.connect(**params)
        cur = conn.cursor()

        listing_insert_sql_query = f"""INSERT INTO listing(title, price, free_shipping, images, url, model, sold, sold_date, seller_id)
            VALUES('{payload["title"]}', {payload["price"]}, {payload["free_shipping"]}, {payload["images"]},
                    '{payload["url"]}', '{payload["model"]}', {payload["sold"]}, '{payload["sold_date"]}', {seller_id}) RETURNING listing_id;"""
        cur.execute(listing_insert_sql_query)
        print("SUCCESS: Created LISTING record")
        listing_id = cur.fetchone()[0]

        description_insert_sql_query = f"""INSERT INTO description(fre_score, avg_grade_score, listing_id)
            VALUES('{payload["fre_score"]}', {payload["avg_grade_score"]}, '{listing_id}');"""
        size_insert_sql_query = f"""INSERT INTO size(shoe_size, adult_shoe, youth_shoe, child_shoe, listing_id)
            VALUES('{payload["shoe_size"]}', {payload["adult_shoe"]}, {payload["youth_shoe"]}, {payload["child_shoe"]},
                    '{listing_id}');"""

        insert_queries = [description_insert_sql_query, size_insert_sql_query]

        for query in insert_queries:
            cur.execute(query)
        print("SUCCESS: Created DESC, SIZE records")

        conn.commit()
        cur.close()
    except Exception as e:
        return(str(e))
    finally:
        if conn is not None:
            conn.close()

    return jsonify(f"Created listing record with listing_id <{listing_id}>")


"""
UPDATE APIs
"""
@app.route("/update_shoe_listing/<listing_id>", methods=['PUT'])
def update_listing(listing_id):
    conn = None
    payload = {
        "title": request.form.get("title"),
        "price": request.form.get("price"),
        "free_shipping": request.form.get("free_shipping"),
        "images": request.form.get("images"),
        "url": request.form.get("url"),
        "model": request.form.get("model"),
        "sold": request.form.get("sold"),
        "sold_date": request.form.get("sold_date")
    }
    
    try:
        params = config()
        conn = psycopg2.connect(**params)
        cur = conn.cursor()

        update_listing_query = f"""UPDATE listing
            SET title = '{payload["title"]}', price = {payload["price"]}, free_shipping = {payload["free_shipping"]},
            images = {payload["images"]}, url = '{payload["url"]}', model = '{payload["model"]}', sold = {payload["sold"]},
            sold_date = '{payload["sold_date"]}'
            WHERE listing_id = '{listing_id}'
            RETURNING listing_id;"""
        cur.execute(update_listing_query)
        conn.commit()
        cur.close()

    except Exception as e:
        return(str(e))
    finally:
        if conn is not None:
            conn.close()
    
    return jsonify(f"SUCCESS: Updated listing record with listing_id <{listing_id}>")

@app.route("/update_seller_record/<seller_id>", methods=['PUT'])
def update_seller_record(seller_id):
    conn = None
    payload = {
        "username": request.form.get("username"),
        "positive": request.form.get("positive"),
        "neutral": request.form.get("neutral"),
        "negative": request.form.get("negative"),
        "join_date": request.form.get("join_date"),
        "followers": request.form.get("followers"),
        "positive_feedback": request.form.get("positive_feedback")
    }

    try:
        params = config()
        conn = psycopg2.connect(**params)
        cur = conn.cursor()

        update_seller_query = f"""UPDATE seller
            SET username = '{payload["username"]}', positive = {payload["positive"]}, neutral = {payload["neutral"]},
            negative = {payload["negative"]}, join_date = '{payload["join_date"]}', followers = {payload["followers"]},
            positive_feedback = {payload["positive_feedback"]}
            WHERE seller_id = '{seller_id}'
            RETURNING seller_id;"""
        cur.execute(update_seller_query)
        conn.commit()
        cur.close()
    except Exception as e:
        return(str(e))
    finally:
        if conn is not None:
            conn.close()
    return jsonify(f"SUCCESS: Updated seller record with seller_id <{seller_id}>")

@app.route("/update_seller_record/username/<username>", methods=['PUT'])
def update_seller_record_by_username(username):
    conn = None
    payload = {
        "username": request.form.get("username"),
        "positive": request.form.get("positive"),
        "neutral": request.form.get("neutral"),
        "negative": request.form.get("negative"),
        "join_date": request.form.get("join_date"),
        "followers": request.form.get("followers"),
        "positive_feedback": request.form.get("positive_feedback")
    }

    try:
        params = config()
        conn = psycopg2.connect(**params)
        cur = conn.cursor()

        update_seller_query = f"""UPDATE seller
            SET username = '{payload["username"]}', positive = {payload["positive"]}, neutral = {payload["neutral"]},
            negative = {payload["negative"]}, join_date = '{payload["join_date"]}', followers = {payload["followers"]},
            positive_feedback = {payload["positive_feedback"]}
            WHERE username = '{username}'
            RETURNING username;"""
        cur.execute(update_seller_query)
        conn.commit()
        cur.close()
    except Exception as e:
        return(str(e))
    finally:
        if conn is not None:
            conn.close()
    return jsonify(f"SUCCESS: Updated seller record with username <{username}>")

@app.route("/update_desc_record/<listing_id>", methods=['PUT'])
def update_description_record(listing_id):
    conn = None
    payload = {
        "fre_score": request.form.get("fre_score"),
        "avg_grade_score": request.form.get("avg_grade_score")
    }

    try:
        params = config()
        conn = psycopg2.connect(**params)
        cur = conn.cursor()

        update_desc_query = f"""UPDATE description
            SET fre_score = '{payload["fre_score"]}', avg_grade_score = {payload["avg_grade_score"]}
            WHERE listing_id = '{listing_id}'
            RETURNING listing_id;"""
        cur.execute(update_desc_query)
        conn.commit()
        cur.close()
    except Exception as e:
        print(str(e))
    finally:
        if conn is not None:
            conn.close()
    return jsonify(f"SUCCESS: Updated description record with listing_id <{listing_id}>")

@app.route("/update_size_record/<listing_id>", methods=['PUT'])
def update_size_record(listing_id):
    conn = None
    payload = {
        "shoe_size": request.form.get("shoe_size"),
        "adult_shoe": request.form.get("adult_shoe"),
        "youth_shoe": request.form.get("youth_shoe"),
        "child_shoe": request.form.get("child_shoe")
    }

    try:
        params = config()
        conn = psycopg2.connect(**params)
        cur = conn.cursor()

        update_size_query = f"""UPDATE size
            SET shoe_size = {payload["shoe_size"]}, adult_shoe = {payload["adult_shoe"]}, youth_shoe = {payload["youth_shoe"]},
            child_shoe = {payload["child_shoe"]}
            WHERE listing_id = '{listing_id}'
            RETURNING listing_id;"""
        cur.execute(update_size_query)
        conn.commit()
        cur.close()
    except Exception as e:
        print(str(e))
    finally:
        if conn is not None:
            conn.close()
    return jsonify(f"SUCCESS: Updated SIZE record with listing_id <{listing_id}>")

"""
READ APIs
"""
@app.route("/GetBulkShoeListings", methods=['GET'])
def get_bulk_shoe_listings():
    listing_records = None
    conn = None
    res = []
    try:
        conn = config()
        cur = conn.cursor()

        listing_sql_query = "SELECT listing_id, seller_id, price, free_shipping, images, sold, sold_date FROM listing;"
        cur.execute(listing_sql_query)
        listing_records = cur.fetchall()
        
        for listing_record in listing_records:
            listing_dict = {
                "price": listing_record[2],
                "free_shipping": listing_record[3],
                "images": listing_record[4],
                "sold": listing_record[5],
                "sold_date": listing_record[6]
            }
            res.append(listing_dict)
        conn.commit()
        cur.close()
    except Exception as e:
        return(str(e))
    finally:
        if conn is not None:
            conn.close()

    return(jsonify(res))

@app.route("/get_listing/<listing_id>", methods=['GET'])
def get_all_listing_records_id(listing_id):
    listing_records = None
    conn = None
    try:
        params = config()
        conn = psycopg2.connect(**params)
        cur = conn.cursor()

        listing_sql_query = f"""SELECT listing_id, seller_id, price, free_shipping, images, sold, sold_date FROM listing
                                where listing_id='{listing_id}';"""
        cur.execute(listing_sql_query)
        listing_records = cur.fetchall()

        conn.commit()
        cur.close()
    except Exception as e:
        return(str(e))
    finally:
        if conn is not None:
            conn.close()

    return(jsonify(listing_records))

@app.route("/GetBulkSellers", methods=['GET'])
def get_all_seller_records():
    seller_records = None
    conn = None
    res = []
    try:
        conn = config()
        cur = conn.cursor()

        seller_sql_query = """SELECT seller_id, username, positive, neutral, negative, join_date,
                                followers, positive_feedback FROM seller;"""
        cur.execute(seller_sql_query)
        seller_records = cur.fetchall()

        for seller_record in seller_records:
            seller_dict = {
                "positive": seller_record[2],
                "neutral": seller_record[3],
                "negative": seller_record[4],
                "join_date": seller_record[5],
                "followers": seller_record[6],
                "positive_feedback": seller_record[7]
            }
            res.append(seller_dict)
        conn.commit()
        cur.close()
    except Exception as e:
        return(str(e))
    finally:
        if conn is not None:
            conn.close()

    return(jsonify(res))

@app.route("/get_seller_record/<username>", methods=['GET'])
def get_seller_record_username(username):
    seller_records = None
    conn = None
    try:
        params = config()
        conn = psycopg2.connect(**params)
        cur = conn.cursor()

        seller_sql_query = f"""SELECT seller_id, username, positive, neutral, negative, join_date,
                                followers, positive_feedback FROM seller where username='{username}';"""
        cur.execute(seller_sql_query)
        seller_records = cur.fetchall()

        conn.commit()
        cur.close()
    except Exception as e:
        return(str(e))
    finally:
        if conn is not None:
            conn.close()

    return(jsonify(seller_records))

@app.route("/get_seller_record_id/<seller_id>", methods=['GET'])
def get_seller_record_id(seller_id):
    seller_records = None
    conn = None
    try:
        params = config()
        conn = psycopg2.connect(**params)
        cur = conn.cursor()

        seller_sql_query = f"""SELECT seller_id, username, positive, neutral, negative, join_date,
                                followers, positive_feedback FROM seller where seller_id='{seller_id}';"""
        cur.execute(seller_sql_query)
        seller_records = cur.fetchall()

        conn.commit()
        cur.close()
    except Exception as e:
        return(str(e))
    finally:
        if conn is not None:
            conn.close()

    return(jsonify(seller_records))

@app.route("/GetDescData", methods=['GET'])
def get_all_desc_records():
    desc_records = None
    conn = None
    res = []
    try:
        conn = config()
        cur = conn.cursor()

        desc_sql_query = "SELECT fre_score, avg_grade_score FROM description;"
        cur.execute(desc_sql_query)
        desc_records = cur.fetchall()

        for desc_record in desc_records:
            desc_dict = {
                "fre_score": desc_record[0],
                "avg_grade_score": desc_record[1],
            }
            res.append(desc_dict)
        conn.commit()
        cur.close()
    except Exception as e:
        return(str(e))
    finally:
        if conn is not None:
            conn.close()

    return(jsonify(res))

@app.route("/GetBulkSizeData", methods=['GET'])
def get_all_size_records():
    size_records = None
    conn = None
    res = []
    try:
        conn = config()
        cur = conn.cursor()

        size_sql_query = "SELECT shoe_size, adult_shoe, youth_shoe, child_shoe FROM size;"
        cur.execute(size_sql_query)
        size_records = cur.fetchall()

        for size_record in size_records:
            size_dict = {
                "shoe_size": size_record[0],
                "adult_shoe": size_record[1],
                "youth_shoe": size_record[2],
                "child_shoe": size_record[3]
            }
            res.append(size_dict)

        conn.commit()
        cur.close()
    except Exception as e:
        return(str(e))
    finally:
        if conn is not None:
            conn.close()

    return(jsonify(res))

"""
DELETE APIs
"""
@app.route("/delete_listing_record/<listing_id>", methods=['DELETE'])
def delete_listing_record(listing_id):
    conn = None
    try:
        params = config()
        conn = psycopg2.connect(**params)
        cur = conn.cursor()

        delete_listing_query = f"""DELETE FROM listing WHERE listing_id = '{listing_id}';"""
        cur.execute(delete_listing_query)
        conn.commit()
        cur.close()
    except Exception as e:
        print(str(e))
    finally:
        if conn is not None:
            conn.close()
    return jsonify(f"SUCCESS: Deleted LISTING record with listing_id <{listing_id}>")

@app.route("/delete_seller/<seller_id>", methods=['DELETE'])
def delete_seller_record(seller_id):
    conn = None
    try:
        params = config()
        conn = psycopg2.connect(**params)
        cur = conn.cursor()

        delete_seller_query = f"""DELETE FROM seller WHERE seller_id = '{seller_id}';"""
        cur.execute(delete_seller_query)
        conn.commit()
        cur.close()
    except Exception as e:
        print(str(e))
    finally:
        if conn is not None:
            conn.close()
    return jsonify(f"SUCCESS: Deleted SELLER record with seller_id <{seller_id}>")

if __name__ == '__main__':
    app.run(host='localhost', port=9874)