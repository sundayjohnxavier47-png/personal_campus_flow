import copy

from campusflow.reports import generate_report
from campusflow.storage import load_tickets, save_tickets
from campusflow.tickets import create_ticket
from campusflow.validation import (
    parse_affected_users,
    validate_category,
    validate_staff_name,
    validate_status,
    validate_title,
    validate_urgency,
)
from campusflow.workflow import (
    assign_ticket,
    change_status,
    find_ticket,
    get_work_queue,
    reopen_ticket,
)

MENU = """
===== CampusFlow =====
1. Create ticket
2. List all tickets
3. View one ticket
4. Assign ticket
5. Change status
6. Reopen ticket
7. Work queue
8. Report
9. Exit
(Tip: press Ctrl+C at any prompt to go back to this menu.)
"""

# Menu choices that change ticket data (and then save it).
MUTATING_CHOICES = {"1", "4", "5", "6"}


def ask(prompt, validator):
    """Keep asking until the validator accepts the answer."""
    while True:
        try:
            return validator(input(prompt))
        except ValueError as error:
            print(f"  Error: {error} Please try again.")


def ask_for_ticket(tickets):
    return ask("Ticket ID: ", lambda text: find_ticket(tickets, text))


def show_ticket(ticket):
    assigned = ticket["assigned_to"] or "unassigned"
    print(
        f'{ticket["id"]} | {ticket["title"]} | {ticket["category"]} | '
        f'urgency: {ticket["urgency"]} | users: {ticket["affected_users"]} | '
        f'priority: {ticket["priority"]} | status: {ticket["status"]} | {assigned}'
    )


def handle_create(tickets):
    title = ask("Title: ", validate_title)
    category = ask("Category (Network/Hardware/Software/Other): ", validate_category)
    urgency = ask("Urgency (low/medium/high): ", validate_urgency)
    affected_users = ask("Affected users: ", parse_affected_users)

    ticket = create_ticket(tickets, title, category, urgency, affected_users)
    save_tickets(tickets)
    print("Created:")
    show_ticket(ticket)


def handle_list(tickets):
    if not tickets:
        print("No tickets yet.")
        return
    for ticket in tickets:
        show_ticket(ticket)


def handle_view(tickets):
    show_ticket(ask_for_ticket(tickets))


def handle_assign(tickets):
    ticket = ask_for_ticket(tickets)

    if ticket["status"] == "resolved":
        print("Error: Resolved tickets must be reopened before changes.")
        return

    staff = ask("Staff member name: ", validate_staff_name)
    ticket = assign_ticket(tickets, ticket["id"], staff)
    save_tickets(tickets)
    print("Assigned:")
    show_ticket(ticket)


def handle_status(tickets):
    ticket = ask_for_ticket(tickets)
    print(f'Current status: {ticket["status"]}')

    if ticket["status"] == "resolved":
        print("Error: Resolved tickets must be reopened first.")
        return

    new_status = ask("New status (in_progress/resolved): ", validate_status)
    ticket = change_status(tickets, ticket["id"], new_status)
    save_tickets(tickets)
    print("Updated:")
    show_ticket(ticket)


def handle_reopen(tickets):
    ticket = ask_for_ticket(tickets)

    if ticket["status"] != "resolved":
        print("Error: Only resolved tickets can be reopened.")
        return

    ticket = reopen_ticket(tickets, ticket["id"])
    save_tickets(tickets)
    print("Reopened:")
    show_ticket(ticket)


def handle_queue(tickets):
    queue = get_work_queue(tickets)
    if not queue:
        print("The work queue is empty.")
        return
    for ticket in queue:
        show_ticket(ticket)


def handle_report(tickets):
    report = generate_report(tickets)
    print(f'Total tickets: {report["total"]}')
    print("By status:")
    for status, count in report["by_status"].items():
        print(f"  {status}: {count}")
    print("By priority:")
    for priority, count in report["by_priority"].items():
        print(f"  {priority}: {count}")


ACTIONS = {
    "1": handle_create,
    "2": handle_list,
    "3": handle_view,
    "4": handle_assign,
    "5": handle_status,
    "6": handle_reopen,
    "7": handle_queue,
    "8": handle_report,
}


def main():
    try:
        tickets = load_tickets()
    except ValueError as error:
        print(f"Error: {error}")
        print("Fix or remove data/tickets.json yourself. Nothing was changed.")
        return

    while True:
        print(MENU)

        try:
            choice = input("Choose an option: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye.")
            break

        if choice == "9":
            print("Goodbye.")
            break

        action = ACTIONS.get(choice)
        if action is None:
            print("Invalid option. Choose 1-9.")
            continue

        # Keep a copy so a failed save can be undone in memory.
        snapshot = copy.deepcopy(tickets) if choice in MUTATING_CHOICES else None

        try:
            action(tickets)
        except ValueError as error:
            print(f"Error: {error}")
        except OSError as error:
            if snapshot is not None:
                tickets[:] = snapshot
            print(f"Error: could not save tickets ({error}). Your last change was undone.")
        except (KeyboardInterrupt, EOFError):
            print("\nCancelled. Back to the menu.")


if __name__ == "__main__":
    main()