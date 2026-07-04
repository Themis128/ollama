# Architecture Documentation

## System Overview

DeepAgents + Ollama Integration is a production-ready coding agent system that combines the power of local LLM inference with sophisticated agent orchestration patterns.

## High-Level Architecture

```mermaid
graph TB
    subgraph "User Interface Layer"
        UI[User Interface]
        CLI[CLI Scripts]
        PP[Project Picker]
    end
    
    subgraph "Agent Orchestration Layer"
        OA[Orchestrator Agent]
        AS[Agent Storm]
        TDD[TDD Agent]
    end
    
    subgraph "Execution Layer"
        TA[Terminal Agent]
        SA[Sandbox Agent]
        WA[Web Agent]
        DA[Debug Agent]
    end
    
    subgraph "Integration Layer"
        DO[DeepAgents Ollama]
        CG[Cloudless.gr Integration]
    end
    
    subgraph "Backend Layer"
        OLLAMA[Ollama Server]
        LLM[Qwen2.5-Coder]
    end
    
    UI --> OA
    CLI --> OA
    PP --> OA
    
    OA --> AS
    OA --> TDD
    OA --> TA
    
    AS --> TA
    AS --> SA
    AS --> WA
    AS --> DA
    
    TDD --> TA
    TDD --> DA
    
    TA --> DO
    SA --> DO
    WA --> DO
    DA --> DO
    
    DO --> CG
    DO --> OLLAMA
    OLLAMA --> LLM
```

## Component Architecture

### 1. Orchestrator Agent

The central coordination hub that manages agent mode switching and task decomposition.

```mermaid
stateDiagram-v2
    [*] --> Architect: Complex Task
    [*] --> Code: Simple Implementation
    [*] --> Debug: Error Reported
    
    Architect --> Code: Plan Ready
    Code --> Debug: Tests Fail
    Debug --> Code: Fix Generated
    Code --> [*]: Success
    Debug --> [*]: Max Iterations
```

**Modes:**
- **Architect Mode**: System design, planning, high-level decisions
- **Code Mode**: Implementation, refactoring, file operations
- **Debug Mode**: Error analysis, log parsing, fix generation
- **Auto Mode**: Automatic mode switching based on task context

### 2. Agent Storm Pattern

Parallel multi-agent execution for comprehensive problem solving.

```mermaid
flowchart LR
    subgraph "Input"
        T[Task]
        P[Prompt]
    end
    
    subgraph "Agent Pool"
        A1[Architect Agent]
        A2[Backend Agent]
        A3[Security Agent]
        A4[Testing Agent]
    end
    
    subgraph "Synthesis"
        S[Synthesizer Agent]
    end
    
    subgraph "Output"
        R[Combined Result]
    end
    
    T --> A1
    T --> A2
    T --> A3
    T --> A4
    P --> A1
    P --> A2
    P --> A3
    P --> A4
    
    A1 --> S
    A2 --> S
    A3 --> S
    A4 --> S
    
    S --> R
```

**Agent Roles:**

| Role | Focus Area | System Prompt Focus |
|------|------------|---------------------|
| Architect | System design, patterns, scalability | High-level structure |
| Backend | API, database, business logic | Implementation details |
| Security | Vulnerabilities, auth, compliance | Security best practices |
| Testing | Coverage, edge cases, automation | Test strategy |
| Frontend | UI, UX, accessibility | Component design |
| DevOps | Infrastructure, deployment, CI/CD | Operational concerns |

### 3. TDD Agent

Test-Driven Development with autonomous self-correction.

```mermaid
flowchart TD
    START[Start] --> RED[RED Phase]
    RED --> |Write Test| TEST1[Test File Created]
    TEST1 --> |Run Test| FAIL[Test Fails ✓]
    FAIL --> GREEN[GREEN Phase]
    GREEN --> |Write Code| IMPL[Implementation Created]
    IMPL --> |Run Test| CHECK{Tests Pass?}
    CHECK --> |Yes| REFACTOR[REFACTOR Phase]
    CHECK --> |No| SELF[Self-Correction Loop]
    SELF --> |Analyze Error| FIX[Generate Fix]
    FIX --> |Apply Fix| IMPL
    REFACTOR --> |Clean Code| VERIFY[Final Verification]
    VERIFY --> SUCCESS[Success ✓]
    SELF --> |Max Iterations| FAIL2[Failed ✗]
```

**Configuration:**

```python
TDDConfig(
    model="qwen2.5-coder",
    base_url="http://localhost:11434",
    project_path="/path/to/project",
    temperature=0.1,          # Low for precise coding
    max_iterations=10,        # Self-correction limit
    timeout=60,               # Per-iteration timeout
)
```

### 4. Terminal & Sandbox Agents

Secure command execution with layered security.

```mermaid
flowchart TD
    CMD[Command Input] --> VAL{Validation}
    VAL --> |Blocked| BLOCK[Blocked ✗]
    VAL --> |Not in Allowlist| BLOCK
    VAL --> |Allowed| ENV[Setup Environment]
    
    ENV --> ISOLATION{Isolation Enabled?}
    ISOLATION --> |Yes| SAFE[Safe Environment]
    ISOLATION --> |No| NORMAL[Normal Environment]
    
    SAFE --> EXEC[Execute Command]
    NORMAL --> EXEC
    
    EXEC --> TIMEOUT{Timeout?}
    TIMEOUT --> |Yes| KILL[Kill Process]
    TIMEOUT --> |No| CAPTURE[Capture Output]
    
    CAPTURE --> AUDIT[Log to Audit]
    AUDIT --> RESULT[Return Result]
```

**Security Layers:**

1. **Command Blocklist**: Dangerous commands always blocked
   - `rm -rf`, `mkfs`, `dd`, `sudo`, `chmod 777`, etc.

2. **Command Allowlist**: Only approved commands allowed
   - `npm`, `pnpm`, `node`, `python`, `git`, `ls`, etc.

3. **Environment Isolation**: Clean environment variables
   - Strips `LD_PRELOAD`, `PYTHONPATH`, etc.
   - Sets minimal `PATH`

4. **Audit Logging**: Complete execution tracking
   - Timestamp, command, exit code, output size
   - Written to `/tmp/sandbox_audit.log`

### 5. Web Agent

Internet communication with safety controls.

```mermaid
flowchart TD
    QUERY[Search Query] --> CACHE{Cache Hit?}
    CACHE --> |Yes| RETURN1[Return Cached]
    CACHE --> |No| RATE{Rate Limit OK?}
    RATE --> |No| WAIT[Wait]
    WAIT --> RATE
    RATE --> |Yes| SAFE{Safe Domain?}
    SAFE --> |No| BLOCK2[Block Request]
    SAFE --> |Yes| FETCH[Fetch URL]
    FETCH --> STORE[Store in Cache]
    STORE --> RETURN2[Return Result]
```

**Safe Domains:**
- `docs.langchain.com`
- `nextjs.org`
- `react.dev`
- `typescriptlang.org`
- `stripe.com`
- `aws.amazon.com`
- `github.com`
- `stackoverflow.com`
- `wikipedia.org`

## Data Flow

### Request Processing Flow

```mermaid
sequenceDiagram
    participant U as User
    participant O as Orchestrator
    participant A as Agent
    participant T as Terminal
    participant S as Sandbox
    participant L as LLM
    
    U->>O: Submit Task
    O->>O: Determine Mode
    
    alt Complex Task
        O->>A: Spawn Agent Storm
        A->>L: Parallel Queries
        L->>A: Multiple Responses
        A->>O: Synthesized Result
    else Simple Task
        O->>A: Single Agent
        A->>L: Query
        L->>A: Response
    end
    
    alt Requires Execution
        A->>T: Command Request
        T->>S: Validate & Execute
        S->>T: Result
        T->>A: Output
    end
    
    A->>O: Final Result
    O->>U: Response
```

### TDD Workflow Sequence

```mermaid
sequenceDiagram
    participant U as User
    participant T as TDD Agent
    participant L as LLM
    participant F as Filesystem
    participant E as Test Runner
    
    U->>T: run_tdd(feature, test_file, impl_file)
    
    Note over T: RED Phase
    T->>L: Generate failing test
    L->>T: Test code
    T->>F: Write test file
    T->>E: Run tests
    E->>T: Tests fail (expected)
    
    Note over T: GREEN Phase
    T->>L: Generate implementation
    L->>T: Implementation code
    T->>F: Write impl file
    T->>E: Run tests
    
    alt Tests pass
        Note over T: REFACTOR Phase
        T->>L: Generate refactored code
        L->>T: Clean code
        T->>F: Update impl file
        T->>U: Success
    else Tests fail
        Note over T: SELF-CORRECT Phase
        loop Max Iterations
            T->>E: Run tests
            E->>T: Error output
            T->>L: Analyze & fix
            L->>T: Fixed code
            T->>F: Update impl file
        end
        T->>U: Result
    end
```

## Integration Points

### DeepAgents SDK Integration

```mermaid
graph LR
    subgraph "Ollama Integration"
        CO[ChatOllama]
        CONFIG[OllamaConfig]
    end
    
    subgraph "DeepAgents SDK"
        DA[create_deep_agent]
        PP[ProviderProfile]
        RP[register_provider_profile]
    end
    
    subgraph "Cloudless.gr"
        SK[Skills]
        SA[Subagents]
        MCP[MCP Servers]
    end
    
    CONFIG --> CO
    CO --> DA
    PP --> RP
    RP --> DA
    
    SK --> DA
    SA --> DA
    MCP --> DA
```

### LangChain Integration

```mermaid
graph TB
    subgraph "LangChain Layer"
        LC[langchain-core]
        LO[langchain-ollama]
    end
    
    subgraph "Model Layer"
        CO[ChatOllama]
        QW[Qwen2.5-Coder]
    end
    
    subgraph "Agent Layer"
        TDD[TDD Agent]
        TA[Terminal Agent]
        OA[Orchestrator]
    end
    
    LC --> LO
    LO --> CO
    CO --> QW
    
    CO --> TDD
    CO --> TA
    CO --> OA
```

## Deployment Architecture

### Local Development

```mermaid
graph TB
    subgraph "Development Machine"
        subgraph "Ollama Folder"
            VENV[Python venv]
            INT[Integrations]
            SCR[Scripts]
        end
        
        subgraph "Ollama Server"
            OLLAMA[Ollama Process]
            MODEL[Qwen2.5-Coder]
        end
        
        subgraph "Target Project"
            PROJ[cloudless.gr]
            SKILLS[.deepagents/skills]
            MCP[.deepagents/.mcp.json]
        end
    end
    
    VENV --> INT
    INT --> OLLAMA
    OLLAMA --> MODEL
    INT --> PROJ
    PROJ --> SKILLS
    PROJ --> MCP
```

### Production Deployment (Future)

```mermaid
graph TB
    subgraph "Load Balancer"
        LB[HAProxy/Nginx]
    end
    
    subgraph "Agent Cluster"
        AG1[Agent Instance 1]
        AG2[Agent Instance 2]
        AG3[Agent Instance N]
    end
    
    subgraph "LLM Backend"
        OLLAMA1[Ollama Node 1]
        OLLAMA2[Ollama Node 2]
    end
    
    subgraph "Storage"
        REDIS[Redis Cache]
        PG[PostgreSQL Audit Log]
    end
    
    LB --> AG1
    LB --> AG2
    LB --> AG3
    
    AG1 --> OLLAMA1
    AG2 --> OLLAMA2
    AG3 --> OLLAMA1
    AG3 --> OLLAMA2
    
    AG1 --> REDIS
    AG2 --> REDIS
    AG3 --> REDIS
    
    AG1 --> PG
    AG2 --> PG
    AG3 --> PG
```

## Configuration Schema

### TDDConfig

```yaml
model: string          # LLM model name
base_url: string       # Ollama server URL
project_path: string   # Target project path
temperature: float     # Generation temperature (0.0-1.0)
max_iterations: int    # Self-correction limit
timeout: int           # Per-iteration timeout (seconds)
```

### TerminalConfig

```yaml
project_path: string   # Working directory
sandbox: bool          # Enable sandbox mode
allowlist: [string]    # Allowed commands
blocklist: [string]    # Blocked commands
timeout: int           # Command timeout
max_retries: int       # Retry attempts
```

### SandboxConfig

```yaml
project_path: string
allow_dangerous: bool
enable_isolation: bool
max_output_size: int
timeout: int
audit_log_path: string
allowlist: [string]
blocklist: [string]
```

### WebConfig

```yaml
rate_limit: int        # Requests per minute
timeout: int           # Request timeout
max_retries: int       # Retry attempts
cache_dir: string      # Cache directory
safe_domains: [string] # Allowed domains
```

### AgentStormConfig

```yaml
model: string
base_url: string
project_path: string
temperature: float
num_agents: int        # Number of parallel agents
max_workers: int       # ThreadPool workers
synthesizer_model: string
timeout: int           # Total timeout
```
