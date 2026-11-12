# Workbench — what I use it for

Workbench is my personal AI agent harness — a workspace for agents, tasks and their results. I build its web console and integrations with AI coding tools, then use them for my own projects and recurring work.

Some tasks run regularly, such as reviewing incoming documents or researching products. Others start when I ask: analysing a budget summary, comparing options or working through a development task. The console gives me a place to follow the work and return to its results.

## Documents and paperwork

I use Paperless to keep my documents. Workbench helps organise what arrives in the inbox.

A daily check prepares text from eligible documents. An agent suggests a useful title, tags, correspondent and document type. The integration checks those suggestions against the original document before applying anything.

Clear cases can be handled under rules I have enabled. An uncertain date, a possible duplicate or a document that needs visual inspection stays for review. After an update, the integration reads back what Paperless actually saved.

This leaves me with organised documents and a smaller set of cases that need a decision.

## Receipts and budget questions

Receipts need a different kind of checking. Codex and Claude read the prepared receipt text independently. Code compares their answers, checks the supporting text and looks for possible matches with transactions.

The result is a review report with matching candidates. Category updates, where permitted, go through a separate integration with Actual Budget.

Budget analysis starts when I request it. I can ask an agent to examine a prepared budget summary and return suggestions for me to review. Questions about purchases or subscriptions follow a similar pattern: I discuss the choice, receive a proposal and decide what to do.

Document organisation, receipt matching and budget analysis are separate jobs. They share information where needed, but each produces its own result.

## Research and comparisons

I also use Workbench for questions that benefit from revisiting sources and keeping the findings together.

| Area | What the work produces |
| --- | --- |
| **Career research** | Vacancy observations and comparisons within a chosen scope, with source links and dates. |
| **Product research** | Updates to a catalogue of products I use, including alternatives, exact variants and prices. |
| **Market watch** | Saved snapshots of new and used asking prices for selected products and configurations. |

Some research runs on a schedule. Larger comparisons can become individual assignments.

Dates matter here. A saved comparison remains useful, but opening it today does not make its prices or listings current. The pages keep source dates visible so I can judge whether the material needs another look.

## Security and home-lab reports

I use Audit, automatic maintenance and Workbench as parts of one process: collect the facts, apply permitted updates, check what changed and analyse what remains.

The cycle starts with a fresh Audit report and the current Wazuh findings. A controller on Cubi checks the registered machines for eligible system-package updates. It works through them one at a time, checking the backup and service state before proceeding.

After updating a machine, it checks the running services. Once the update stage is complete, it collects fresh security observations and checks which CVEs have been fixed. Workbench then analyses the remaining findings and adds explanations and possible next steps.

The update list comes from the package manager and rules I have approved. The agents help interpret what remains after those updates.

Zenarmor reports follow a separate path: Workbench reviews saved network observations and returns an explanation tied to that report.

[How the Audit and maintenance cycle works](workbench-internals.md#audit-updates-and-remaining-cves)

## Larger tasks with a small team

For a larger assignment, I can ask Workbench to divide the work between agents.

I describe the goal and what a useful result should contain. A planning step divides the task, individual agents work on their parts, and a final step brings the findings together.

From the console, I can follow the stages and open an individual conversation if it needs my attention. The result comes back to the original assignment, alongside the criteria I set.

I use the same interface for a single assistant when splitting the task would add little.

## Data collection behind the pages

Several parts of the workspace use ordinary collectors and calculations.

| Area | What happens |
| --- | --- |
| **Fitness** | Garmin and TrainHeroic data is collected and used to calculate summaries for my private fitness pages. |
| **Events** | Venue programmes become listings with source dates and coverage. A separate calendar connection helps me compare events with work commitments. |
| **Home observation** | Selected Home Assistant states are checked for availability problems and changes that may need attention. |
| **Infrastructure audit** | Scheduled checks collect information about the machines and services in the lab. |

These processes provide useful information without calling a model for every update. An agent can then help with a specific question where interpretation adds value.

## Working with the results

The console separates current assignments, conversations, history and recurring workflows. I can see what is still running, what has produced an answer and what needs a decision.

Work runs on the server, so my browser and Mac do not need to stay open. Results remain attached to their conversations, and I can continue from them later.

Questions and problems needing my attention are sent promptly. Routine results and documentation updates are grouped into a daily digest.

The part I keep developing is this connection between a request and a usable result: giving agents the right material, checking their work and making it easy to return to what they have done.

**[How Workbench works — the console, agents and task execution](workbench-internals.md)**

[Back to the home lab overview](../README.md)
