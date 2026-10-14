# CampusFlow

A command-line helpdesk ticket manager for Learn2Earn campus staff. It records technical problems (Wi-Fi outages, faulty laptops, broken software), calculates how urgent each one is, assigns it to a staff member, tracks its progress, and saves everything to a JSON file.

## Team

- codeMinaa: ticket creation, input validation and the priority engine (campusflow/tickets.py, tests/test_tickets.py)
- sundayjohnxavier47-png: assignment, status workflow, work queue, reports, JSON storage and the CLI menu (campusflow/workflow.py, reports.py, storage.py, main.py and their tests)

## Setup

- Python 3 (standard library only, no packages to install)
- Clone the repo and open the project folder:

    git clone https://github.com/codeMinaa/campus-flow.git
    cd campus-flow

## Run the app

    python3 main.py

Menu options:

1. Create ticket
2. List all tickets
3. View one ticket
4. Assign ticket
5. Change status
6. Reopen ticket
7. Work queue
8. Report
9. Exit

## Run the tests

    python3 -m unittest discover -s tests -v

The tests cover ticket creation and validation, all four priority levels, assignment, status transitions, the work queue order, reports (including zero tickets), and JSON saving, reloading and corrupted files.

## Ticket rules

Allowed categories: Network, Hardware, Software, Other. Allowed urgency: low, medium, high. The title cannot be blank and affected users must be a positive whole number.

Priority is checked in this order, and the first match wins:

1. High urgency and 10 or more affected users: critical
2. High urgency or 10 or more affected users: high
3. Medium urgency or 3 or more affected users: medium
4. Anything else: low

Status flow: open, then in_progress, then resolved.
- A ticket must be assigned before it can move to in_progress.
- A resolved ticket cannot be changed until it is reopened (which sets it back to open).

The work queue lists open tickets from critical to low. Tickets with the same priority are ordered by ticket number.

## Where tickets are saved

Tickets are saved to data/tickets.json and loaded when the app starts. If the file is missing, the app starts fresh. If the file is corrupted, the app shows an error and does not overwrite it. To start fresh, delete data/tickets.json.

## Known limitations

- Text-only interface, no GUI
- Staff names are free text
- The work queue shows only open tickets, not in_progress ones
- Tickets cannot be edited or deleted after creation

## Pull requests

- Ticket creation and validation: https://github.com/codeMinaa/campus-flow/pull/1
- Assignment, workflow, queue and reports: https://github.com/codeMinaa/campus-flow/pull/3
- JSON persistence and CLI menu: 

This is a personal copy of a team project. The original repository is https://github.com/codeMinaa/campus-flow, built with codeMinaa. See the Team section for who wrote what.