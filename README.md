# SubLang: The LLM-Native Way to _Write_ Software

[![Discord Chat](https://img.shields.io/discord/1382712250598690947?logo=discord)](https://discord.gg/Tv4EcTu5YX)

We share the vision that large language models (LLMs) will enable people to build and maintain software using natural language.
This will dramatically unleash human productivity, making it easier to turn great ideas into reality.

However, the current approaches fall short of realizing this vision:
- Having non-developers describe high-level requirements in a few sentences for AI to generate prototypes.
  This path ultimately runs into **the wall of completeness and maintainability** — vague language lacks the information needed for building complete and maintainable software.
- Having professional developers direct an AI teammate to generate code.
  This path ultimately hits **the wall of requirement and design knowledge** — AI lacks comprehensive understanding of software requirements and system design.

The walls exist because software requirements, design, and implementation speak different languages:
- requirements are expressed in ambiguous natural language;
- design is captured in formal notations like UML (Unified Modeling Language); and
- implementation is written in programming languages.

To overcome these walls, the right approach is to unify requirements, design, and implementation in a well-defined natural language — enabling LLMs to reason across the full software development lifecycle.

> Every program is a well-defined sublanguage.

## Definition

A **well-defined sublanguage** (WDSL, for short) expresses the composition and behavior of software in a controlled form of natural language.
A WDSL consists of the following three components.

### Term

Terms define the essential concepts of the software, such as users, labels, and thumbs-up.
These terms form the building blocks of the software structure.
Additionally, software behavior can be represented as sequences of events or operations, all expressed using these defined terms.

### Syntax

Syntax specifies the constraints governing software behavior.
For example, `permission` must be granted before editing a `label`.

### Semantics

Semantics refer to meaningful sequences or patterns of software behavior that define specific features of the system.
For example, sharing a file may involve updating file `permission`, adding a `collaborator` mapping between the file and the user, and sending a `notification` to the user.
These semantic definitions serve as the foundation for test cases and enable automated verification.

## Join Us
- Chat: [https://discord.gg/Tv4EcTu5YX](https://discord.gg/Tv4EcTu5YX)
- Forum: [https://github.com/orgs/welldefined-ai/discussions](https://github.com/orgs/welldefined-ai/discussions)
