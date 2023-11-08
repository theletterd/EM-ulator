import random

from em_ulator import db


class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)


    @staticmethod
    def create_new_game():
        game = Game()
        db.session.add(game)
        db.session.commit()
        return game


    def exists(game_id):
        game = Game.query.filter_by(id=game_id).first()
        return bool(game)

    def get_all_tickets(game_id):
        # probably a better way to do this.
        projects = Project.query.filter_by(game_id=game_id).all()
        project_ids = [project.id for project in projects]
        tickets = Ticket.query.filter(
            Ticket.project_id.in_(project_ids)
        ).order_by(Ticket.id.asc()).all()

        return tickets


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
    ticket_offset = db.Column(db.Integer, nullable=False)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'))
    game = db.relationship('Game')



class Ticket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    project = db.relationship('Project')
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.String(2048), nullable=False)

    # e.g., JIRA-1234
    key = db.Column(db.String(120), unique=True, nullable=False)
    #state_id = db.Column(db.Integer, db.ForeignKey('ticketstate.id'), nullable=False)
    #state = db.relationship('TicketState')

    @staticmethod
    def new_ticket(project, title, description):
        num_existing_tickets = Ticket.query.filter_by(project_id=project.id).count()
        # how many tickets are already in this project?
        # let's just say 100 for now
        # we can do counting later.
        ticket_id = num_existing_tickets + 1 + project.ticket_offset
        key = f"{project.name}-{ticket_id}"
        ticket = Ticket(
            project_id=project.id,
            key=key,
            title=title,
            description=description
        )

        db.session.add(ticket)
        db.session.commit()




class TicketState(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    # e.g., "Open", "In Progress", "Blocked", "Closed"
    name = db.Column(db.String(120), unique=True, nullable=False)

    # store the 6-character hex-value
    color = db.Column(db.String(6), nullable=False)
