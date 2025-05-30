

from flask import Flask, jsonify, render_template, request,Response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Boolean , Float
from random import choice
import json

from sqlalchemy.orm.base import attribute_str

app = Flask(__name__)

class Base(DeclarativeBase):
    pass

app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///cafes.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)

class Cafe(db.Model):
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    name: Mapped[str] = mapped_column(String(100),unique=True,nullable = False)
    map_url: Mapped[str] = mapped_column(String(500),nullable=False)
    img_url: Mapped[str] = mapped_column(String(500),nullable=False)
    location: Mapped[str] = mapped_column(String(150),nullable=False)
    coffee_price: Mapped[float] = mapped_column(Float(7),nullable=False)
    seats: Mapped[int]  = mapped_column(Integer,nullable=False)
    has_sockets: Mapped[bool] = mapped_column(Boolean,nullable=False)
    has_toilet: Mapped[bool] = mapped_column(Boolean,nullable=False)
    has_wifi: Mapped[bool] = mapped_column(Boolean,nullable=False)
    can_take_calls: Mapped[bool] = mapped_column(Boolean,nullable=False)
    

    def to_dict(self):
        return {
            "id": self.id,
            "name":self.name,
            "map_url":self.map_url,
            "img_url":self.img_url,
            "location":self.location,
            "coffee_price":self.coffee_price,
            "seats":self.seats,
            "has_sockets":self.has_sockets,
            "has_toilet":self.has_toilet,
            "has_wifi":self.has_wifi,
            "can_take_calls":self.can_take_calls,
        }



with app.app_context():
    db.create_all()


@app.route("/",methods=["GET"])
def home():
    return render_template("index.html")

''' route random cafe'''


@app.route("/random",methods=["GET"])
def random():
    result = db.session.execute(db.select(Cafe))
    all_cafes = result.scalars().all()
    random_cafe = choice(all_cafes)
    cafe_data = {
        "id" : random_cafe.id,
        "name": random_cafe.name,
        "map_url": random_cafe.map_url,
        "img_url": random_cafe.img_url,
        "location": random_cafe.location,
        "has_sockets": random_cafe.has_sockets,
        "has_toilet": random_cafe.has_toilet,
        "has_wifi": random_cafe.has_wifi,
        "can_take_calls": random_cafe.can_take_calls,
        "seats": random_cafe.seats,
        "coffee_price": random_cafe.coffee_price
    }

    return Response(json.dumps({"cafe":cafe_data},indent=2),mimetype='application/json')


''' route all the cafes'''


@app.route("/all",methods=["GET"])
def all_cafes():
    result = db.session.execute(db.select(Cafe).order_by(Cafe.name))
    all_cafes = result.scalars().all()


    return jsonify(cafes=[cafe.to_dict() for cafe in all_cafes ])


''' route search cafe by location'''
@app.route("/search",methods=["GET"])
def search_cafe():
    query_location = request.args.get("loc")
    result = db.session.execute(db.select(Cafe).where(Cafe.location==query_location))
    all_cafes = result.scalars().all()

    if all_cafes:
        return jsonify(cafes=[cafe.to_dict() for cafe in all_cafes])

    else:
        return jsonify(error={"Not found":"Sorry! no cafe found for the particular location"}),404

''' route for adding new cafe'''


@app.route("/add", methods=["POST"])
def add_cafe():
    try:
        new_cafe = Cafe(
            name=request.form.get("name"),
            map_url=request.form.get("map_url"),
            img_url=request.form.get("img_url"),
            location=request.form.get("location"),
            has_sockets=request.form.get("has_sockets") == "True",
            has_toilet=request.form.get("has_toilet") == "True",
            has_wifi=request.form.get("has_wifi") == "True",
            can_take_calls=request.form.get("can_take_calls") == "True",
            seats=int(request.form.get("seats")),
            coffee_price=float(request.form.get("coffee_price"))
        )

        db.session.add(new_cafe)
        db.session.commit()
        return jsonify(response={"success": "Cafe added successfully"}), 201

    except Exception as e:
        return jsonify(error={"unsuccessful": "Could not add cafe", "details": str(e)}), 400

'''Update coffee price'''
@app.route("/update-price/<int:cafe_id>",methods=["PATCH"])
def update_price(cafe_id):
    new_price = request.args.get("new_price")
    try:
        cafe = db.session.get(Cafe,cafe_id)
    except AttributeError:
        return jsonify(error={"error","No cafe with cafe id found in the database"}),404

    cafe.coffee_price = new_price
    db.session.commit()
    return jsonify(error={"Successful":"Coffee Price edited successfully"})


'''' Deleting a cafe with cafe_Id'''

@app.route("/delete/<int:cafe_id>",methods=["DELETE"])
def delete_cafe(cafe_id):
    api_key = request.args.get("api_key")

    if api_key == "topsecretkey":
        cafe = db.session.get(Cafe,cafe_id)

        if cafe is None:
            return jsonify(error={"Not found":"We did not find any cafe in the database"}),404

        db.session.delete(cafe)
        db.session.commit()
        return jsonify(error={"Successfull":"Deleted cafe from the database"}),200
    else:
        return jsonify(error={"Not authorised":"You are not authorised to access the database"}),400



if __name__ == "__main__":
    app.run(debug=True)