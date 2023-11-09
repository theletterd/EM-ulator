import random
import string

from em_ulator import db
from em_ulator import config


class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ticks_elapsed = db.Column(db.Integer, nullable=False, default=0)

    def percent_complete(self):
        tickets = self.get_all_tickets()
        num_tickets = len(tickets)
        num_complete_tickets = len(list(filter(lambda t: t.state_id is TicketState.CLOSED, tickets)))
        return 100 * (num_complete_tickets / num_tickets)

    @staticmethod
    def create_new_game():
        game = Game()
        db.session.add(game)
        db.session.commit()
        return game

    def get_game(game_id):
        game = Game.query.filter_by(id=game_id).first()
        return game

    def get_all():
        games = Game.query.all()
        return games

    def get_all_tickets(self):
        # probably a better way to do this.
        projects = Project.query.filter_by(game_id=self.id).all()
        project_ids = [project.id for project in projects]
        tickets = Ticket.query.filter(
            Ticket.project_id.in_(project_ids)
        ).order_by(Ticket.id.asc()).all()

        return tickets

    # maybe we don't tick the tickets, we increase the game tick,
    # and record the last transition tick on the ticket instead.

    def tick(self):
        self.ticks_elapsed += 1
        db.session.add(self)
        db.session.commit()

        # ok motherfucker
        # we need to get the employees
        employees = Employee.query.filter_by(game_id=self.id)

        for employee in employees:
            remaining_effort = employee.productivity
            # maybe we need a ticket percentage complete
            # maybe the ticks are hours, not days?
            # ok so we need review sub-states
            # Needs review
            # Being Reviewed
            # are deploys done by one person?
            # bug rotation
            # Deployable

            # get tasks
            # which is
            # Do reviews
            #

            # OKOKOKOKOK


            # really there should only be only one in-progress ticket, but who knows where
            # we'll end up.
            while remaining_effort > 0:
                in_progress_tickets = Ticket.get_assigned_in_progress_tickets(employee.id)

                if not in_progress_tickets:
                    # get_next_ticket
                    ticket = Ticket.assign_new_ticket(employee.id)
                    if ticket:
                        print(f"{employee.name} picked up {ticket.key}")
                        continue
                    else:
                        # if no more tickets... "waiting state"
                        print(f"{employee.name} is waiting for more work.")
                        remaining_effort = 0
                        continue


                for ticket in in_progress_tickets:
                    effort_to_expend = min(remaining_effort, ticket.remaining_work)
                    ticket.do_work(effort_to_expend)
                    remaining_effort -= effort_to_expend
                    print(f"{employee.name} worked on {ticket.key}")
                    if ticket.remaining_work == 0:
                        ticket.move_to_review()
                        print(f"{employee.name} put {ticket.key} out for review")

            # Are there any tickets that are in progress?
            # if so, burn them down and move to in-review if appropriate
            # if not, assign the next ticket.

            # we'll deal with reviews later.

            # OKOKOKOKOK

            # Do work
            #
            # ok is there a review loop we need to worry about?
            # no we can avoid it if we pretend there's one round of reviews only
            # so
            # reviewing costs points
            #   only review tickets that are assigned to you
            # when a review is done, reviewer adds work
            # while remaining_points:
            #   remaining points go towards current ticket
            #   if no more work left on ticket, move to review
            #   if there's points remaining, pick up another ticket
            #take a break
            pass

        #tickets = self.get_all_tickets()
        #for ticket in tickets:
        #    ticket.transition()

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

    def new_project(game_id):
        random_project_name = ''.join(random.sample(string.ascii_uppercase, random.randrange(3, 8)))
        project = Project(
            name=random_project_name,
            ticket_offset=random.randrange(1000),
            game_id=game_id
        )
        db.session.add(project)
        db.session.commit()
        return project




class Ticket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    project = db.relationship('Project')
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.String(2048), nullable=False)
    original_sizing = db.Column(db.Integer, nullable=False)
    remaining_work = db.Column(db.Integer, nullable=False)
    update_tick = db.Column(db.Integer, nullable=False, default=0)

    # e.g., JIRA-1234
    key = db.Column(db.String(120), unique=True, nullable=False)
    assignee_id = db.Column(db.Integer, db.ForeignKey('employee.id'))
    assignee = db.relationship('Employee', lazy='joined')
    state_id = db.Column(db.Integer, db.ForeignKey('ticket_state.id'), nullable=False)
    state = db.relationship('TicketState', lazy='joined')

    @staticmethod
    def new_ticket(project_id):
        project = Project.query.filter_by(id=project_id).first()
        num_existing_tickets = Ticket.query.filter_by(project_id=project.id).count()

        # how many tickets are already in this project?
        # let's just say 100 for now
        # we can do counting later.
        ticket_id = num_existing_tickets + 1 + project.ticket_offset
        key = f"{project.name}-{ticket_id}"
        size = random.randrange(100)
        ticket = Ticket(
            project_id=project.id,
            key=key,
            title=random.choice(config.ticket_names),
            description="ehhhhh",
            original_sizing=size,
            remaining_work=size,
            state_id=TicketState.OPEN,
            update_tick=project.game.ticks_elapsed
        )

        db.session.add(ticket)
        db.session.commit()



    @property
    def is_closed(self):
        return self.state_id == TicketState.CLOSED

    def move_to_review(self):
        self.state_id = TicketState.IN_REVIEW
        self.update_tick = self.project.game.ticks_elapsed
        db.session.add(self)
        db.session.commit()

    def do_work(self, effort):
        self.remaining_work -= effort
        db.session.add(self)
        db.session.commit()

    def assign_new_ticket(employee_id):
        unassigned_open_tickets = Ticket.get_unassigned_open_tickets()
        if not unassigned_open_tickets:
            return None

        ticket = random.choice(unassigned_open_tickets)
        ticket.assignee_id = employee_id
        ticket.state_id = TicketState.IN_PROGRESS
        db.session.add(ticket)
        db.session.commit()

        return ticket

    def get_unassigned_open_tickets():
        tickets = Ticket.query.filter(
            Ticket.assignee_id.is_(None),
            Ticket.state_id == TicketState.OPEN
        ).all()
        return tickets

    def get_assigned_in_progress_tickets(employee_id):
        tickets = Ticket.query.filter(
            Ticket.assignee_id == employee_id,
            Ticket.state_id == TicketState.IN_PROGRESS
        ).all()
        return tickets

    def transition(self):
        # clamp the tick count to a range
        # self.tick_count = min(self.tick_count + 1, 20)
        self.tick_count += 1

        # maybe we should randomly generate a size and use that as a probability to transition
        probability = 0.25
        # or maybe on each tick some number of points is distrubuted among in-progress tickets.
        # this could get complex, so let's figure that out after the UI stuff.
        # with some probability, move the ticket forward.
        if (not self.is_closed) and (random.random() < probability):
            self.state_id = self.state.next_state_id
            self.tick_count = 0

            self.mutate()

        db.session.add(self)
        db.session.commit()


    def mutate(self):
        # instead of transitioning forward, something terrible has happened
        # and we've gone to some state previously defined.
        probability = 0.01
        if random.random() < probability:
            #self.state_id = random.randrange(self.state_id)
            self.state_id = TicketState.BLOCKED
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


class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(1024), nullable=False)
    productivity = db.Column(db.Integer, nullable=False)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'))
    game = db.relationship('Game')

    def new_employee(game_id):

        first_name = random.choice(config.first_names)
        last_name = random.choice(config.last_names)

        employee = Employee(
            name=f"{first_name} {last_name}",
            productivity=random.randrange(20),
            game_id=game_id
        )

        db.session.add(employee)
        db.session.commit()
        return employee
