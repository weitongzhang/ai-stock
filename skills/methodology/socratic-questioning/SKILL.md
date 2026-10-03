---
name: socratic-questioning
description: Use this skill at the start of user requests when intent, assumptions, goals, constraints, risk tolerance, definitions, or success criteria are unclear. It applies Socratic questioning to clarify what the user means and what decision they need before analysis, recommendations, implementation, trading judgment, planning, or problem solving. Use especially when a premature answer could be misleading, costly, risky, or misaligned with the user's actual thinking.
---

# Socratic Questioning

## Role

Use this skill as a clarification layer before solving. Help the user make their own idea sharper by asking disciplined questions, reflecting the current understanding, and stopping once the information is sufficient to act.

Default to the user's language.

## Core Rule

Ask before concluding when any of these are unclear:

- The user's real objective.
- The decision they are trying to make.
- Key definitions or terms of art.
- Timeframe, constraints, risk tolerance, or acceptable trade-offs.
- Evidence the user already has.
- What would count as a good answer or successful outcome.

Do not ask questions just to appear thorough. If the request is already clear and low risk, answer directly and briefly state the assumption.

## Workflow

1. **Reflect the request**
   - Restate the user's question in one sentence.
   - Name the decision or ambiguity you think matters most.

2. **Ask a small question set**
   - Ask 1-3 focused questions at a time.
   - Prefer questions that change the answer.
   - Avoid long questionnaires.

3. **Probe assumptions**
   - Ask what the user believes is true and what would disprove it.
   - Separate facts, interpretations, preferences, and fears.

4. **Clarify constraints**
   - Identify timeframe, budget, position size, tools, deadlines, downside limit, or other boundaries.
   - For trading or risk-bearing tasks, always clarify current position, cost, intended holding period, and maximum acceptable loss if missing.

5. **Summarize and confirm**
   - Briefly summarize the clarified picture.
   - If still uncertain, ask the next most important question.
   - Once sufficient, say the working assumptions and proceed.

## Question Patterns

Use the smallest useful subset:

- **Goal**: "你这次最想解决的是判断方向、制定操作，还是校准我的分析框架？"
- **Definition**: "你说的‘强’具体指板块涨幅、前排封板、资金持续性，还是可操作性？"
- **Evidence**: "你现在依据的是盘口、K线、消息，还是你自己的交易模型？"
- **Alternative**: "如果这个判断错了，最可能错在哪里？"
- **Trade-off**: "你更怕卖飞，还是更怕利润回撤？"
- **Constraint**: "这笔操作是日内、隔日，还是波段？最大能接受回撤多少？"
- **Success**: "回答到什么程度，你会觉得可以执行？"

## Stop Conditions

Stop asking and start solving when:

- The objective and decision are clear.
- The material constraints are known or reasonably assumed.
- Additional questions would not materially change the answer.
- The user asks for a direct answer after enough context has been gathered.

When proceeding with assumptions, label them clearly.

## Guardrails

- Do not hide uncertainty behind confidence.
- Do not turn every small request into a long interview.
- Do not ask the user to provide information that can be obtained from local files, tools, or data sources.
- Do not use leading questions to force the user toward your preferred conclusion.
- For urgent, time-sensitive, or high-stakes requests, ask only the highest-impact clarifying question, then give a conditional answer.
