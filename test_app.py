import pytest
from unittest.mock import MagicMock
from bson import ObjectId
from app import app
from models import Pet

@pytest.fixture
def mock_mongo(mocker):
    mock_mongo = MagicMock()

    # mocking database methods
    mock_mongo.db.pets.insert_one = MagicMock()
    mock_mongo.db.pets.find = MagicMock()
    mock_mongo.db.pets.find_one = MagicMock()
    mock_mongo.db.pets.update_one = MagicMock()

    app.mongo = mock_mongo
    return mock_mongo


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as testing_client:
        yield testing_client


# ------------------TESTS ----------------------------------
# ===== miserable, PLS DO NOT CHANGE =========================

def test_get_by_id(client, mock_mongo):
    # find_one method to return a specific pet by ID
    mock_pet_id = str(ObjectId())
    mock_mongo.db.pets.find_one = MagicMock(return_value={
        'name': 'Sisu',
        'pet_type': 'Dog',
        'age': 4,
        'species': 'Finnish Spitz',
        'adopted': False,
        '_id': ObjectId(mock_pet_id)
    })

    # get_by_id with valid id string
    pet = Pet.get_by_id(app.mongo, mock_pet_id)

    assert pet['name'] == 'Sisu'


def test_update_adoption_status(client, mocker, mock_mongo):
    # update_one method to mock updating the adoption status
    mock_pet_id = str(ObjectId())  # Generate a valid ObjectId string
    mock_mongo.db.pets.update_one = MagicMock()

    # Create a pet instance
    pet = Pet(name="Sisu", pet_type="Dog", age=4, species="Finnish Spitz")

    # Update the adoption status for the mock pet
    pet.update_adoption_status(app.mongo, mock_pet_id)

    # Assert that update_one was called with the correct data
    mock_mongo.db.pets.update_one.assert_called_once_with(
        {'_id': ObjectId(mock_pet_id)},  # Use the valid ObjectId
        {'$set': {'adopted': True}}
    )


def test_save_to_db(client, mock_mongo):
    # create a pet
    pet = Pet(name="Sisu", pet_type="Dog", age=4, species="Finnish Spitz")
    pet.save_to_db(app.mongo)
    mock_mongo.db.pets.insert_one.assert_called_once_with({
       'name': 'Sisu',
       'type': 'Dog',
       'age': 4,
       'species': 'Finnish Spitz',
       'adopted': False
    })


def test_get_all(client, mock_mongo):
    # find method to return a list of pets
    mock_mongo.db.pets.find = MagicMock(return_value=[{
        'name': 'Sisu',
        'pet_type': 'Dog',
        'age': 4,
        'species': 'Finnish Spitz',
        'adopted': False
   }])

    pets = Pet.get_all(app.mongo)

    assert len(pets) == 1
    assert pets[0]['name'] == 'Sisu'

 # -----------------------------------


#DELETE TEST
def test_delete_pet(client, mock_mongo):
    mock_pet_id = str(ObjectId())

    # insert mock pet to database
    mock_mongo.db.pets.insert_one({
        '_id': ObjectId(mock_pet_id),
        'name': 'Sisu',
        'pet_type': 'Dog',
        'age': 4,
        'species': 'Finnish Spitz',
        'adopted': False
    })

    # mock the find_one method to return inserted pet before deletion
    mock_mongo.db.pets.find_one = MagicMock(return_value={
        '_id': ObjectId(mock_pet_id),
        'name': 'Sisu',
        'pet_type': 'Dog',
        'age': 4,
        'species': 'Finnish Spitz',
        'adopted': False
    })

    response = client.post(f"/delete_pet/{mock_pet_id}")

    # redirect
    assert response.status_code == 302
    assert response.location == '/pets'

    # after delete, mock find_one to return none, pet is deleted
    mock_mongo.db.pets.find_one = MagicMock(return_value=None)

    # checks pet is not in database
    remaining_pet = mock_mongo.db.pets.find_one({'_id': ObjectId(mock_pet_id)})
    assert remaining_pet is None

# RESULTS: 5 Passed in 8.68s
