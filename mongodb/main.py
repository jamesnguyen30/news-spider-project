# tutorial: https://www.youtube.com/watch?v=E-1xI85Zog8

# before deploy to production. Take the author's other course where he show how to setup linux server in production

import mongoengine
from schemas.owners import Owners
from schemas.houses import Houses
from schemas.bookings import Bookings
from datetime import datetime, timedelta

# connect('mydb', host='localhost', port=27017)

def init_mongoengine():
    mongoengine.register_connection(alias='core', name='mydb')

    print("initiated")

def create_owner():
    name = str(input("Owner name: "))
    owner = Owners()
    owner.name = name
    owner.save()
    return owner

def list_owner():
    owners = Owners.objects()
    return owners

def get_owner_by_name(name: str) -> Owners:
    owner = Owners.objects(name = name).first()
    return owner

def create_house():
    house = Houses()
    house.type = str(input("Enter house type:"))
    house.rooms = int(input("Enter house rooms:"))
    house.name = str(input("Enter name for this house:"))
    house.address = str(input("Enter the address for this house:"))

    house.save()

    print("Choose the owner")
    owner_name = str(input("Enter owner name:"))

    owner = get_owner_by_name(owner_name)

    if owner != None:
        owner.house_ids.append(house.id)
        owner.save()
        print(f"Created a new house with id = {house.id} for owner: {owner_name}")
    else:
        print("Owner now found!")

def list_houses():
    houses = Houses.objects()
    return houses

def list_bookings() -> list():
    bookings = bookings.objects()
    return bookings

def create_booking():
    print("choose the owner you want to book with")
    owners = list_owner()

    for index, owner in enumerate(owners):
        print(f'{index}. {owner.name}')
    
    opt = int(input("Select your owner: "))

    selected_owner = owners[opt]

    print("select house your want:")
    house_ids = selected_owner.house_ids

    for index, house_id in enumerate(house_ids):
        id = str(house_id)
        house = Houses.objects(id = id).first()
        print(f'{index}. {house.address}')
    
    opt = int(input("Select house: "))

    selected_house_id = house_ids[opt]

    booking = Bookings()
    booking.owner_id = selected_owner.id
    booking.house_id = selected_house_id
    today = datetime.now()
    booking.checkin_date = today 
    booking.checkout_date = today + timedelta(days = 3)

    selected_owner.bookings.append(booking)
    selected_owner.save()

def print_menu():
    print("OPTIONS")
    print("1. list owners")
    print("2. create owner")
    print("3. list houses")
    print("4. create house")
    print("5. list bookings")
    print("6. create bookings")
    print("7. exit")

def init():
    mongoengine.register_connection(alias='core', name='fake_airbnb')

if __name__ == '__main__':

    init_mongoengine()

    is_running = True
    while is_running:

        print_menu()
        opt = int(input("Enter your options:"))
        if opt == 1:
            list_owner()
            print()
        if opt == 2:
            owner = create_owner()
            print("SUCCESS: ", owner)
        if opt == 3:
            houses = list_houses()
            for house in houses:
                print(f"type: {house.type}")
                print(f"rooms: {house.rooms}")
                print(f"address: {house.address}")
            
            print()
        if opt == 4:
            create_house()
        if opt == 5:
            bookings = list_bookings()

            for b in bookings:
                print(f'owner id: {b.guests_id}')
                print(f'house id: {b.house_id}')
                print(f'bookd date: {b.booked_date}')
                print(f'checkin date: {b.checkin_date}')
                print(f'checkout date: {b.checkout_date}')
            
        if opt == 6:

            create_booking()
        if opt == 7:
            is_running = False

    print("end of program")