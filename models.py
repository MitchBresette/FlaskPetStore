# models.py

from bson.objectid import ObjectId


# pet constructor
class Pet:
    def __init__(self, name, pet_type, age, species, adopted=False):
        self.name = name
        self.pet_type = pet_type
        self.age = age
        self.species = species
        self.adopted = adopted

    def save_to_db(self, mongo):
        pet_data = {
            'name': self.name,
            'type': self.pet_type,
            'age': self.age,
            'species': self.species,
            'adopted': self.adopted
        }
        mongo.db.pets.insert_one(pet_data)

    # get all pets
    @staticmethod
    def get_all(mongo):
        pets = mongo.db.pets.find()
        return [pet for pet in pets]

    # get pet by ID
    @staticmethod
    def get_by_id(mongo, pet_id):
        pet = mongo.db.pets.find_one({'_id': ObjectId(pet_id)})
        return pet

    # sets adopted to true
    def update_adoption_status(self, mongo, pet_id):
        mongo.db.pets.update_one({'_id': ObjectId(pet_id)}, {'$set': {'adopted': True}})