from main import db

class Flight(db.Model):
    __tablename__ = 'flights'

    id = db.Column(db.Integer, primary_key=True)
    flight_type = db.Column(db.String())
    journey = db.Column(db.String())
    stopover = db.Column(db.String())
    airline = db.Column(db.String())
    airline_logo = db.Column(db.String())
    flight_number = db.Column(db.String())
    status = db.Column(db.String())
    scheduled_time = db.Column(db.String())
    estimated_time = db.Column(db.String())

    def __init__(self, flight_type, journey, stopover, airline, airline_logo, flight_number, status, scheduled_time, estimated_time):
        self.flight_type = flight_type
        self.journey = journey
        self.stopover = stopover
        self.airline = airline
        self.airline_logo = airline_logo
        self.flight_number = flight_number
        self.status = status
        self.scheduled_time = scheduled_time
        self.estimated_time = estimated_time

    def __repr__(self):
        return '<flight number {}>'.format(self.flight_number)

    def serialise(self):
        return {
            'id': self.id,
            'flight_type': self.flight_type,
            'journey': self.journey,
            'stopover': self.stopover,
            'airline': self.airline,
            'airline_logo': self.airline_logo,
            'flight_number': self.flight_number,
            'status': self.status,
            'scheduled_time': self.scheduled_time,
            'estimated_time': self.estimated_time
        }
