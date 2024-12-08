from flask import Flask, request, render_template, redirect, url_for, jsonify
from flask_pymongo import PyMongo
import os
from dotenv import load_dotenv
from bson.objectid import ObjectId  # mongoDB objectIDs

# env for mongo db
load_dotenv()

app = Flask(__name__)

# --------------mongo db--------------------------------

# login credentials for mongo db connection string from .env
db_username = os.getenv("DB_USERNAME")
db_password = os.getenv("DB_PASSWORD")

# Mongo db connection string (python 6 or newer) -> cluster 0 -> PetStore
app.config[
    "MONGO_URI"] = f"mongodb+srv://{db_username}:{db_password}@cluster0.8sk8t.mongodb.net/PetApp?retryWrites=true&w=majority&appName=Cluster0"
mongo = PyMongo(app)

# console logs connection to mongo db
try:
    mongo.db.command('ping')
    print("Connected to MongoDB")
except Exception as e:
    print(f"Error connecting to MongoDB: {e}")

# --------------------------------------------------


# INDEX
@app.route('/')
def home():
    return render_template('index.html')


# PETS
@app.route('/pets')
def show_pets():
    pets = mongo.db.pets.find()  # fetch all pets from the database
    pet_list = []

    for pet in pets:
        pet['_id'] = str(pet['_id'])
        pet_list.append(pet)

    # checks if pets are available, returns message if not, message used in /pets truthy
    if not pet_list:
        return render_template('pets.html', message="Sorry, no pets available for adoption.")

    return render_template('pets.html', pets=pet_list)


# ADD PETS
@app.route('/add_pets', methods=['GET', 'POST'])
def add_pets():
    """
    Allows users to add a new pet to the database.
    """
    if request.method == 'POST':
        name = request.form.get('name')
        pet_type = request.form.get('pet_type')
        age = request.form.get('age')
        species = request.form.get('species')

        # Validate the age input
        if not age.isdigit() or int(age) < 0:
            return render_template('add_pets.html', error="Age cannot be less than zero")

        # Add pet to the database
        mongo.db.pets.insert_one({
            'name': name,
            'pet_type': pet_type,
            'age': int(age),
            'species': species,
            'adopted': False
        })
        return redirect(url_for('show_pets'))

    return render_template('add_pets.html')


# ADOPT PET
@app.route('/adopt/<pet_id>', methods=['GET', 'POST'])
def adopt_pet(pet_id):
    pet = mongo.db.pets.find_one({'_id': ObjectId(pet_id)})

    if request.method == 'POST':
        if pet:
            if pet['adopted']:
                return render_template('adopt.html', message="Sorry, this pet has already been adopted", pet=pet)

            # Mark pet as adopted
            mongo.db.pets.update_one({'_id': ObjectId(pet_id)}, {'$set': {'adopted': True}})
            return render_template('adopt.html', message=f"Pet {pet['name']} has been successfully adopted!", pet=pet)

        return render_template('adopt.html', message="Pet not found")

    return render_template('adopt.html', pet=pet)


# DELETE
@app.route('/delete_pet/<pet_id>', methods=['POST'])
def delete_pet(pet_id):
    """
    Deletes a pet from the database based on its ID.
    """
    mongo.db.pets.delete_one({'_id': ObjectId(pet_id)})

    # checks if any pets in database
    remaining_pets = mongo.db.pets.count_documents({})

    # redirect to the pets page
    if remaining_pets == 0:
        # if no pets shows message instead
        return redirect(url_for('show_pets', message="Sorry, no pets available for adoption."))
    else:
        # displays pets list
        return redirect(url_for('show_pets'))


if __name__ == '__main__':
    app.run(debug=True)
