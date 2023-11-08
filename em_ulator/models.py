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


    def get_game(game_id):
        game = Game.query.filter_by(id=game_id).first()
        return game

    def get_all_tickets(self):
        # probably a better way to do this.
        projects = Project.query.filter_by(game_id=self.id).all()
        project_ids = [project.id for project in projects]
        tickets = Ticket.query.filter(
            Ticket.project_id.in_(project_ids)
        ).order_by(Ticket.id.asc()).all()

        return tickets


    def tick(self):
        tickets = self.get_all_tickets()
        for ticket in tickets:
            ticket.transition()

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
    tick_count = db.Column(db.Integer, nullable=False, default=1)

    # e.g., JIRA-1234
    key = db.Column(db.String(120), unique=True, nullable=False)
    state_id = db.Column(db.Integer, db.ForeignKey('ticket_state.id'), nullable=False)
    state = db.relationship('TicketState', lazy='joined')

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
            description=description,
            state_id=TicketState.OPEN
        )

        db.session.add(ticket)
        db.session.commit()


    def transition(self):
        # no transitioning Closed tickets.
        if self.state_id == TicketState.CLOSED:
            return

        # maybe we should randomly generate a size and use that as a probability to transition
        probability = 0.25
        # or maybe on each tick some number of points is distrubuted among in-progress tickets.
        # this could get complex, so let's figure that out after the UI stuff.
        # with some probability, move the ticket forward.
        if random.random() < probability:
            self.state_id = self.state.next_state_id
            self.tick_count = 0
        else:
            self.tick_count += 1

        self.mutate()

        db.session.add(self)
        db.session.commit()


    def mutate(self):
        # instead of transitioning forward, something terrible has happened
        # and we've gone to some state previously defined.
        probability = 0.01
        if random.random() < probability:
            self.state_id = random.randrange(self.state_id)
            self.tick_count = 0

        db.session.add(self)
        db.session.commit()


class TicketState(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    # e.g., "Open", "In Progress", "Blocked", "Closed"
    name = db.Column(db.String(120), unique=True, nullable=False)

    # store ticket transition data
    next_state_id = db.Column(db.Integer, db.ForeignKey('ticket_state.id'), nullable=False)
    next_state = db.relationship('TicketState')

    # store the 6-character hex-value
    color = db.Column(db.String(6), nullable=False)

    # proper jank
    BLOCKED = 0
    OPEN = 1
    IN_PROGRESS = 2
    IN_REVIEW = 3
    CLOSED = 4


    def initialise_ticket_states():
        TicketState.query.delete()
        ticket_states = [
            blocked := TicketState(id=TicketState.BLOCKED, name="Blocked", color="#d51643"),
            open := TicketState(id=TicketState.OPEN, name="Open", color="#6540c6"),
            in_progress := TicketState(id=TicketState.IN_PROGRESS, name="In Progress", color="#ff9900"),
            in_review := TicketState(id=TicketState.IN_REVIEW, name="In Review", color="#2c8b93"),
            closed := TicketState(id=TicketState.CLOSED, name="Closed", color="#12a451")
        ]
        blocked.next_state_id = open.id
        open.next_state_id = in_progress.id
        in_progress.next_state_id = in_review.id
        in_review.next_state_id = closed.id
        closed.next_state_id = closed.id

        db.session.add_all(ticket_states)
        db.session.commit()
