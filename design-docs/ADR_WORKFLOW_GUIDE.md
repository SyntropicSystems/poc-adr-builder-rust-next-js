# ADR Creation - Quick Reference

## What You Get

1. **Protobuf Schema** (`adr.proto`): Machine-readable structure for ADRs
2. **Workflow** (`adr_creation_workflow.yaml`): Step-by-step process for creating ADRs
3. **Structured Output**: Both human-readable (markdown) and machine-readable (protobuf) ADRs

## Minimum Workflow Steps

### 1. Identify Problem (Human)
**Input**: A problem that needs a decision  
**Output**: Clear problem statement with impact and scope

```
Questions to answer:
- What's the problem? (one sentence)
- Why does it matter? (impact)
- What level? (strategic/architectural/tactical)
- What breaks if not solved?
```

### 2. Research Options (AI)
**Input**: Problem statement  
**Output**: Minimum 3 analyzed options

```
AI researches and documents:
- Option A, B, C (minimum)
- Pros and cons for each
- Key tradeoffs
- Research references
```

### 3. Analyze Tradeoffs (Human)
**Input**: All options  
**Output**: Understanding of tradeoffs

```
Consider:
- Project constraints
- Team skills
- Reversibility
- Long-term implications
```

### 4. Make Decision (Human)
**Input**: Options analysis  
**Output**: Chosen option with rationale

```
Document:
- Which option
- Why this one
- Why not others
- Key tradeoff accepted
```

### 5. Define Success (AI)
**Input**: Decision  
**Output**: Success criteria and metrics

```
Creates:
- 3-7 testable success criteria
- Quantitative metrics (numbers)
- Qualitative metrics (feedback)
```

### 6. Define Triggers (AI)
**Input**: Decision and metrics  
**Output**: Evidence-based revisit conditions

```
Creates:
- 3-5 observable triggers
- Conditions that indicate revisit needed
- NOT time-based ("review in 6 months")
- Evidence-based ("coupling detected")
```

### 7. Assess Risks (Human)
**Input**: Decision  
**Output**: Risk assessment and migration costs

```
Documents:
- Risks of chosen option
- Mitigation strategies
- Migration cost to alternatives
- Rollback cost
```

### 8. Generate Document (AI)
**Input**: All gathered information  
**Output**: Structured ADR (markdown + protobuf)

```
Creates:
- adr-{id}.md (human-readable)
- adr-{id}.proto (machine-readable)
- All sections populated
```

### 9. Review (Human)
**Input**: Generated ADR  
**Output**: Approval or change requests

```
Checks:
- Problem clear?
- Options well-analyzed?
- Decision rational?
- Success measurable?
- Triggers observable?
```

### 10. Finalize (Human)
**Input**: Approved ADR  
**Output**: Active ADR in registry

```
Actions:
- Status: draft → active
- Add to registry
- Notify stakeholders
- Set up monitoring
```

## Key Principles

### ✅ DO
- Keep problem statement to ONE clear sentence
- Research minimum 3 options
- Make triggers evidence-based (observable conditions)
- Define measurable success criteria
- Document migration costs

### ❌ DON'T
- Make time-based triggers ("review in 6 months")
- Skip option analysis
- Choose without documenting rationale
- Forget to define success metrics
- Ignore risks and migration costs

## Example: Quick ADR

```yaml
Problem: "How do we structure multiple CLI tools?"

Options:
  A: Monolithic binary (simple, inflexible)
  B: Separate binaries (flexible, inconsistent)
  C: Workspace + libraries (balanced)

Decision: Option C
Rationale: "Balance of independence and consistency"

Success Criteria:
  - ✅ Can build any tool independently
  - ✅ Tools share patterns via framework
  - ✅ Adding tool takes < 30 minutes

Metrics:
  - Build time < 30s per tool
  - Coupling = 0 (framework only)
  - Time to add tool < 30 min

Triggers:
  - Tool coupling detected
  - Adding tool takes > 2 hours
  - Workspace build > 2 minutes

Risks:
  - Workspace complexity (Low)
  - Library API maintenance (Medium)
```

## Workflow Integration

### For Humans
```bash
# Start workflow
workflow start adr.creation.v1 \
  --param problem_domain=architecture \
  --param urgency=normal

# Follow prompts through each step
# Workflow guides you through all sections
```

### For AI Assistants
```
Role assignments:
- ai_assistant: Research, analysis, document generation
- human_architect: Problem definition, decision, risk assessment
- reviewer: Quality check

Token scopes:
- Read: existing_adrs, research references
- Write: scratch notes, final documents
- Net: Read only (for research)
```

## Output Files

```
outputs/
├── adr-P1.1.md              # Human-readable ADR
├── adr-P1.1.proto           # Machine-readable ADR
└── adr-P1.1-research.md     # Research notes (scratch)
```

## Quality Checks

The workflow enforces:
- ✅ Minimum 3 options analyzed
- ✅ Decision rationale > 100 characters
- ✅ 3-7 success criteria defined
- ✅ 3-5 revisit triggers defined
- ✅ Peer review completed
- ✅ All required sections present

## Anti-Patterns to Avoid

1. **Analysis Paralysis**: More than 5 options gets overwhelming
2. **Time-based Triggers**: "Review in Q3" → Use "Performance degrades" instead
3. **Vague Success Criteria**: "Works well" → Use "Build time < 30s" instead
4. **No Migration Plan**: Document how to change course
5. **Skip Review**: Always get a second pair of eyes

## Next Steps

After creating an ADR:
1. Set up monitoring for metrics
2. Add to project dashboard
3. Reference in code/docs as "Per ADR-XXX"
4. Schedule first metrics review (when triggers suggest)
5. Update when triggers fire

---

**Remember**: An ADR is a living document. When triggers fire, create a new ADR that supersedes this one!
