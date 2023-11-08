from em_ulator import db

class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)


    @staticmethod
    def create_new_game():
        game = Game()
        db.session.add(game)
        db.session.commit()


    def tick(self):
        self.generate_tickets()
        self.transition_unfinished_tickets()


    def generate_tickets(self):
        pass


    def transition_unfinished_tickets(self):
        pass


class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)




class Ticket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    project = db.relationship('Project')

    # e.g., JIRA-1234
    key = db.Column(db.String(120), unique=True, nullable=False)
    #state_id = db.Column(db.Integer, db.ForeignKey('ticketstate.id'), nullable=False)
    #state = db.relationship('TicketState')




class TicketState(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    # e.g., "Open", "In Progress", "Blocked", "Closed"
    name = db.Column(db.String(120), unique=True, nullable=False)

    # store the 6-character hex-value
    color = db.Column(db.String(6), nullable=False)
