from app import db


class Prediction(db.Model):
    __tablename__ = 'predictions'
    id = db.Column(db.Integer, unique=True, primary_key=True,
                   autoincrement=True)
    response_time = db.Column(db.DateTime)
    recorded_time = db.Column(db.DateTime)
    line_ref = db.Column(db.String, index=True)
    direction_ref = db.Column(db.String, index=True)
    stop_point_ref = db.Column(db.Integer, index=True)
    scheduled_arrival_time = db.Column(db.DateTime)
    expected_arrival_time = db.Column(db.DateTime)

    def __repr__(self):
        return f'<Stop: {self.stop_point_ref} Line: {self.line_ref}>'



