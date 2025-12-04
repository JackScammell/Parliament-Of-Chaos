# Plan Project

You are initiating a project planning session using the **project-oracle** agent.

## Purpose

Guide the user from an initial idea through a structured Q&A process to create a complete project definition with:
- Project outline
- Feature implementation plan
- Development roadmap

## Instructions

1. **Check for existing project files**:
   - Look for `.project-files/` directory
   - If it exists, ask user if they want to:
     - Continue/update the existing project
     - Start fresh (will archive existing files)

2. **Invoke the project-oracle agent** to conduct the interview:
   - Follow the progressive disclosure pattern (Context, Scope, Technical, Timeline, Confirm)
   - Ask one phase of questions at a time
   - Do not rush - gather enough information for a solid project definition

3. **Generate artifacts** once the user confirms the summary:
   - Create `.project-files/` directory if needed
   - Generate `project-outline.md`
   - Generate `feature-implementation.md`
   - Generate `Roadmap.md`

4. **Provide next steps**:
   - Explain that roadmap items can be scoped with `/roadmap-item-scope <item>`
   - Mention that `/project-status` shows overall progress

## Interaction Style

- Be conversational and encouraging
- Take time to understand the user's vision
- Reflect back what you hear to confirm understanding
- Offer examples and suggestions when the user seems stuck
- Do not generate files until the user explicitly confirms the summary is accurate

## Arguments

This command takes an optional argument:

- No argument: Start fresh Q&A session
- With description: Use the provided description as starting context

Example:
- `/plan-project` - Start interactive planning
- `/plan-project Build a task management app for small teams` - Start with context
