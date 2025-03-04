# Define prompt templates
REFINE_PROMPT = """
You are an expert software architect. Please refine and improve the following project description.
Fix any typos, clarify ambiguous points, and ensure it's comprehensive.

Original description:
{raw_input}

Provide a well-structured and clear description.
"""
ARCH_GEN_PROMPT = """
You are a senior software architect with expertise in designing scalable, maintainable systems. Based on the following project description, create a comprehensive software architecture that balances technical excellence with practical implementation considerations.

PROJECT DESCRIPTION:
{refined_description}

Deliver a professional-grade architecture specification with the following sections:

## 1. CORE COMPONENTS
* Identify all primary system components (services, interfaces, data stores)
* Specify the responsibility of each component
* Determine component boundaries and interfaces

## 2. COMPONENT RELATIONSHIPS
* Define clear interaction patterns between components
* Specify communication protocols (REST, GraphQL, message queues, etc.)
* Identify synchronous vs. asynchronous interactions
* Document dependency directions and cardinality

## 3. TECHNOLOGY STACK
* Select appropriate technologies for each component
* Justify key technology selections with rationale
* Consider infrastructure requirements (cloud services, containers, etc.)
* Address cross-cutting concerns (logging, monitoring, security)

## 4. DATA FLOW
* Map the journey of data through the system
* Document data transformations between components
* Identify potential bottlenecks or high-throughput areas
* Address data persistence strategies and caching needs

## 5. INTEGRATION POINTS
* Define external system interfaces
* Specify API contracts and documentation standards
* Address authentication and authorization requirements
* Outline error handling and resilience patterns

## 6. DEPLOYMENT CONSIDERATIONS
* Recommend deployment topologies
* Address scalability and high-availability requirements
* Consider CI/CD pipeline requirements
* Document environment-specific configurations

Ensure your architecture supports key quality attributes including scalability, security, maintainability, and performance based on the project requirements.
"""
ARCH_UPDATE_PROMPT = """
You are a senior software architect tasked with refining an existing architecture based on stakeholder feedback. Apply your expertise to thoughtfully incorporate the feedback while maintaining architectural integrity and coherence.

CURRENT ARCHITECTURE:
{architecture_spec}

STAKEHOLDER FEEDBACK:
{human_feedback}

Provide a revised architecture specification that addresses the feedback while maintaining system cohesion. Your updated architecture must include:

## 1. CORE COMPONENTS
* Update component definitions based on feedback
* Add, modify, or remove components as needed
* Highlight changes from the original architecture with a brief rationale

## 2. COMPONENT RELATIONSHIPS
* Revise interaction patterns to address feedback
* Update communication protocols if necessary
* Ensure relationships remain consistent and logical

## 3. TECHNOLOGY STACK
* Revise technology selections based on feedback
* Justify any new or modified technology choices
* Ensure technology choices remain compatible across the system

## 4. DATA FLOW
* Update data flow patterns to accommodate changes
* Address any performance or scalability concerns raised
* Ensure data consistency across modified components

## 5. INTEGRATION POINTS
* Revise external interfaces based on feedback
* Update API contracts as needed
* Ensure authentication and authorization remain robust

## 6. DEPLOYMENT CONSIDERATIONS
* Update deployment recommendations based on feedback
* Address any scalability or availability concerns raised
* Revise environment configuration recommendations if needed

For each significant change, provide a brief explanation of how it addresses the stakeholder feedback while maintaining architectural best practices.
"""


MERMAID_PROMPT = """
You are a Mermaid.js diagram expert. Transform the following architecture specification into valid, clean Mermaid.js code that prioritizes simplicity and visual clarity.

Architecture Specification to transform:
{architecture_spec}

Follow these strict guidelines to produce error-free Mermaid.js code:

1. DIAGRAM DECLARATION
- Begin with exactly `flowchart TD` (top-down) (left-to-right)
- Do not include any text, comments or styling before this declaration

2. SYNTAX AND FORMATTING RULES
- End EVERY statement with a semicolon (;)
- No spaces in node IDs - use camelCase (e.g., userInterface not user Interface)
- No ellipsis (...) or special characters in the diagram
- Format node labels using square brackets: `nodeId["Display Text"];`
- For database nodes, use cylinder shape: `databaseId[(Database Name)];`
- Close all subgraphs with `end;` (with semicolon)

3. COMPONENT RELATIONSHIPS
- Define relationships AFTER all nodes and subgraphs
- Simple arrow syntax only: `nodeA --> nodeB;` (with semicolon)
- Relationship definitions must not contain spaces between nodes and arrows

4. STYLE DEFINITIONS
- Define styles AFTER diagram type declaration but BEFORE nodes:
  ```
  classDef service fill:#f9f,stroke:#333,stroke-width:2px;
  classDef database fill:#f96,stroke:#333,stroke-width:2px;
  classDef external fill:#ccf,stroke:#333,stroke-width:2px;
  ```
- Apply styles AFTER all nodes and relationships are defined:
  `class nodeId service;`

5. SUBGRAPH STRUCTURE
```
subgraph groupName["Display Name"]
    node1["Node 1"];
    node2["Node 2"];
end;
```

6. VERIFICATION STEPS
Before submitting your answer, validate your code against these common errors:
- Every statement ends with a semicolon
- No spaces in node IDs
- No spaces in relationship arrows
- No dangling relationships to undefined nodes
- No unclosed subgraphs
- No special characters in node IDs

Provide ONLY the complete, valid Mermaid.js code. Do not include explanations, comments, or additional text outside the code.
"""