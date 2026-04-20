# Rheonics Support Chatbot — Product Brief

**Version:** 1.0
**Owner:** Abel Brayan Mancilla Montesinos
**Date:** April 2026

---

## 1. Problem it solves

When a client asks a technical question during or after a meeting, I have to
search through multiple PDFs manually to find the answer. This takes time and
breaks the conversation flow. Also, when I have to diagnose a failure I need
to search all the documentation, and sometimes my boss asks tricky questions
I don't know how to respond to.

## 2. Who uses it

- **User**: Abel (Support Engineer at Rheonics)
- **When**: During client calls, after meetings, internal research
- **Where**: Desktop app, open in background during Teams calls

## 3. What it does (in scope)

- Answers technical questions about Rheonics products and their configuration
- Retrieves specs, ranges, ordering codes
- Explains operating principles
- Suggests compatible accessories
- Identifies which business type/application a given product is ideal for,
  and what physical challenges the application presents
- Creates a summary of the conversation

## 4. What it does NOT do (out of scope)

- Does not answer questions outside Rheonics products
- Does not make pricing decisions
- Does not connect to live Rheonics systems
- Does not remember conversation history between sessions *(Phase 2)*
- Does not process images from Teams/meetings *(Phase 4, via Prompter)*

## 5. What a perfect answer looks like

**Q:** What is the viscosity range of the SRD?
**A:** The SRD measures viscosity from 1 to 3,000 cP (standard range). A wider
range is available on request.

**Q:** What is cP?
**A:** *(answer grounded in the documentation)*

**Q:** Why isn't the sensor turning on?
**A:** I need more context to help diagnose this. Could you share an image of
the sensor or any error code shown on the display? In the meantime, common
causes are: [list from documentation].

## 6. What a bad answer looks like

- Gives a spec that isn't in the documents (hallucination)
- Says "I don't know" when the answer is clearly in the PDFs
- Gives an answer that is technically correct but too vague to be useful
- Uses specs from a different product by mistake
- Mixes imperial and metric units inconsistently

## 7. Tone and persona

- Sounds like: a senior Rheonics support engineer — precise and technical
- Does NOT sound like: a generic assistant, overly friendly, or vague
- When unsure: says "I don't have enough information in my documents to
  confirm this" — never guesses on specs

## 8. Success criteria for MVP

- [ ] Answers 80% of common product questions correctly from documents
- [ ] Never hallucinates a specification
- [ ] Responds in under 3 seconds
- [ ] Handles at least 20 test questions from the benchmark list
- [ ] Graceful fallback when answer is not in knowledge base

## 9. Connection to Prompter app (future)

The Prompter app will feed client process context (fluid type, industry,
conditions) into this chatbot so answers become client-specific, not just
generic product answers.
