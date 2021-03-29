# EECS116/CS122A
# Winter 2021
# MP2 - Python + MySQL Demo Program
# Student Name : Jason Nguyen
# Student ID : 54414997

import pymysql

db = pymysql.connect(
    host='localhost',
    user='mp2',
    password='eecs116',
    db='flights'
)
cur = db.cursor()
userInput = ""
while (userInput != "exit"):
    print("List Of Queries/Tasks: ", 
    "Queries:",
    "Find the cheapest flight given airports and a date",
    "Find the flight and seat information for a customer",
    "Find all non-stop flights for an airline",
    "Tasks:",
    "Add a new airplane",
    "Increase low-cost fares(≤ 200) by a factor",
    "Remove a seat reservation", 
    sep = "\n")
    userInput = input("Which query/task would you like to complete? ")                          # obtains input for which query/task user would like to complete
    if (userInput == "Find the cheapest flight given airports and a date"):
        departureCode = input("Please enter the airport code for the departure airport: ")      # obtains input for departure airport code
        arrivalCode = input("Please enter the airport code for the destination airport: ")      # obtains input for arrival airport code
        flightDate = input("What is the date of the flight in yyyy-mm-dd? ")                    # obtains date of flight
        sql = '''
            WITH possibleFlights(flight_number) AS
            (
            SELECT li.flight_number as flightNumber
            FROM  leg_instance as li
            WHERE li.departure_airport_code = %s AND li.arrival_airport_code = %s AND li.leg_date = %s
            GROUP BY flight_number
            )
            SELECT pf.flight_number as flightNumber, min(f.amount) as cheapestFlight
            FROM possibleFlights as pf, fare as f
            WHERE pf.flight_number = f.flight_number
              '''
        cur.execute(sql, (departureCode, arrivalCode, flightDate))
        cheapestFlight = cur.fetchall()
        if cheapestFlight[0] == (None, None):
            print("No flight exists for departure and arrival airport on given flight date")
        else:
            for row in cheapestFlight:
                print(f"The cheapest flight is {row[0]}, and the cost is ${row[1]}")           #  prints the cheapest flight for given departure/arrival airport codes

    elif (userInput == "Find the flight and seat information for a customer"):
        customerName = input("Please enter the customer's name: ")                              # obtains input for customer name
        sql = '''
            SELECT sr.flight_number as flightNumber, sr.seat_number as seatNumber
            FROM seat_reservation as sr
            WHERE sr.customer_name = %s
        '''
        cur.execute(sql, (customerName))
        for row in cur.fetchall():
            print(f"The flight number is {row[0]}, and the seat number is {row[1]}")            # prints flight number and seat number for customer

    elif (userInput == "Find all non-stop flights for an airline"):
        airline = input("What is the name of the airline? ")                                    # obtains name of airline
        sql = '''
        WITH flightsForGivenAirline(flight_number, numOfLegs) AS (
        SELECT f.flight_number, count(fl.flight_number)
        FROM flight as f, flight_leg as fl
        WHERE f.flight_number = fl.flight_number AND f.airline = %s
        GROUP BY f.flight_number
        )
        SELECT ffga.flight_number
        FROM flightsForGivenAirline as ffga, flight_leg as fl
        WHERE ffga.flight_number = fl.flight_number AND fl.leg_number < 2 AND ffga.numOfLegs < 2
        '''
        cur.execute(sql, (airline))                                                          # finds all non-stop flights given airline
        airlines = cur.fetchall()
        if airlines == ():
            print("No non-stop flights.")
        else:
            print("The non-stop flights are: ")
            for row in airlines:
                print(f"{row[0]}")

    elif (userInput == "Add a new airplane"):
        currentAirplaneId = None
        totalNumSeats = input("Please enter the total number of seats: ")                       # obtains total number of seats for new airplane entry
        airplaneType = input("Please enter the airplane type: ")                                # obtains airplane type for new airplane entry
        sql1 = '''
        SELECT max(a.airplane_id)
        FROM airplane as a
        '''
        cur.execute(sql1)
        for row in cur.fetchall():
            currentAirplaneID = row                                                           
        currentAirplaneID = currentAirplaneID[0] + 1                                            # finds the most recent airplane ID and increments by 1 for new entry
        sql2 = '''
        INSERT INTO airplane(airplane_id,total_number_of_seats,airplane_type) 
        VALUES(%s,%s,%s)
        '''
        cur.execute(sql2, (currentAirplaneID, totalNumSeats, airplaneType))                     # inserts new airplane entry into table
        db.commit()                                                                             # commits entry into database
        print(f"The new airplane has been added with id: {currentAirplaneID}")                  # prints most recent airplane ID entry

    elif (userInput == "Increase low-cost fares(≤ 200) by a factor"):
        lowCostFaresCount = None
        increaseFactor = input("Please enter a factor: ")                                       # obtains input for factor to increase low-cost fares
        sql1 = '''
        SELECT count(f.amount)
        FROM fare as f
        WHERE f.amount <= 200
        '''
        cur.execute(sql1)
        for row in cur.fetchall():
            lowCostFaresCount = row
        lowCostFaresCount = lowCostFaresCount[0]                                                # obtains the amount of tuples that are low cost fares and will be affected
        sql2 = f'''
        UPDATE fare
        SET fare.amount = fare.amount + fare.amount * {increaseFactor}
        WHERE fare.amount <= 200
        '''
        cur.execute(sql2)                                                                       # updates fare amounts
        db.commit()                                                                             # commits update into database
        print(f"{lowCostFaresCount} fares are affect.")                                         # print the amount of tuples that were affected

    elif (userInput == "Remove a seat reservation"):
        seatNumber = None
        flightNumber = input("Please enter the flight number: ")                                # obtains input for flight number
        customerName = input("Please enter the customer name: ")                                # obtains input for customer name
        sql1 = '''w
        SELECT sr.seat_number
        FROM seat_reservation as sr
        WHERE sr.flight_number = %s AND sr.customer_name = %s
        '''
        cur.execute(sql1, (flightNumber, customerName))                                         # obtains seat number given flight number and customer name
        for row in cur.fetchall():
            seatNumber = row
        seatNumber = seatNumber[0]
        sql2 = '''
        DELETE FROM seat_reservation 
        WHERE seat_reservation.flight_number = %s AND seat_reservation.customer_name = %s
        '''
        cur.execute(sql2, (flightNumber, customerName))                                         # deletes seat reservation given flight number and customer name
        db.commit()                                                                             # commits delete to database
        print(f"Seat {seatNumber} is released")                                                 # prints the seat number that was released

    elif (userInput == "exit"):
        break

db.close()