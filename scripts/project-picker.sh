#!/bin/bash
# Project Picker UI for DeepAgents + Ollama
# Automatically scans /home/tbaltzakis for projects

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/.."

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Base directory to scan
SCAN_DIR="/home/tbaltzakis"

# Project indicators (files/folders that indicate a project)
PROJECT_INDICATORS=(
    "package.json"
    "pyproject.toml"
    "requirements.txt"
    "Cargo.toml"
    "go.mod"
    "pom.xml"
    "build.gradle"
    "composer.json"
    "Gemfile"
    ".git"
    ".deepagents"
)

# Function to check if directory is a project
is_project() {
    local dir="$1"
    
    for indicator in "${PROJECT_INDICATORS[@]}"; do
        if [ -e "$dir/$indicator" ]; then
            return 0
        fi
    done
    
    return 1
}

# Function to detect project type
get_project_type() {
    local dir="$1"
    
    if [ -f "$dir/package.json" ]; then
        if [ -f "$dir/next.config.js" ] || [ -f "$dir/next.config.mjs" ]; then
            echo "Next.js"
        elif [ -f "$dir/nuxt.config.js" ]; then
            echo "Nuxt.js"
        elif [ -f "$dir/vue.config.js" ]; then
            echo "Vue.js"
        elif [ -f "$dir/angular.json" ]; then
            echo "Angular"
        elif grep -q '"react"' "$dir/package.json" 2>/dev/null; then
            echo "React"
        else
            echo "Node.js"
        fi
    elif [ -f "$dir/pyproject.toml" ]; then
        if grep -q "fastapi" "$dir/pyproject.toml" 2>/dev/null; then
            echo "FastAPI"
        elif grep -q "django" "$dir/pyproject.toml" 2>/dev/null; then
            echo "Django"
        elif grep -q "flask" "$dir/pyproject.toml" 2>/dev/null; then
            echo "Flask"
        else
            echo "Python"
        fi
    elif [ -f "$dir/requirements.txt" ]; then
        echo "Python"
    elif [ -f "$dir/Cargo.toml" ]; then
        echo "Rust"
    elif [ -f "$dir/go.mod" ]; then
        echo "Go"
    elif [ -f "$dir/pom.xml" ]; then
        echo "Java/Maven"
    elif [ -f "$dir/build.gradle" ]; then
        echo "Java/Gradle"
    elif [ -f "$dir/composer.json" ]; then
        echo "PHP"
    elif [ -f "$dir/Gemfile" ]; then
        echo "Ruby"
    elif [ -d "$dir/.git" ]; then
        echo "Git Repo"
    elif [ -d "$dir/.deepagents" ]; then
        echo "DeepAgents"
    else
        echo "Unknown"
    fi
}

# Function to scan for projects
scan_projects() {
    declare -A found_projects
    
    echo -e "${CYAN}Scanning $SCAN_DIR for projects...${NC}"
    echo ""
    
    # Scan immediate subdirectories
    for item in "$SCAN_DIR"/*; do
        if [ -d "$item" ]; then
            local name=$(basename "$item")
            
            # Skip hidden directories and common non-project directories
            case "$name" in
                .*|node_modules|venv|.venv|__pycache__|.cache|tmp|temp)
                    continue
                    ;;
            esac
            
            # Check if it's a project
            if is_project "$item"; then
                local project_type=$(get_project_type "$item")
                found_projects["$name"]="$item|$project_type"
            fi
        fi
    done
    
    # Also check nested projects (one level deeper for common patterns)
    for item in "$SCAN_DIR"/*/*; do
        if [ -d "$item" ]; then
            local parent=$(basename "$(dirname "$item")")
            local name=$(basename "$item")
            
            # Skip hidden and common non-project directories
            case "$name" in
                .*|node_modules|venv|.venv|__pycache__|.cache|tmp|temp|src|lib|dist|build)
                    continue
                    ;;
            esac
            
            if is_project "$item"; then
                local full_name="$parent/$name"
                local project_type=$(get_project_type "$item")
                found_projects["$full_name"]="$item|$project_type"
            fi
        fi
    done
    
    # Store results globally
    PROJECTS_FOUND=()
    PROJECT_PATHS=()
    PROJECT_TYPES=()
    
    # Sort projects alphabetically
    IFS=$'\n' sorted=($(for key in "${!found_projects[@]}"; do echo "$key"; done | sort))
    unset IFS
    
    for name in "${sorted[@]}"; do
        local value="${found_projects[$name]}"
        local path="${value%%|*}"
        local type="${value##*|}"
        
        PROJECTS_FOUND+=("$name")
        PROJECT_PATHS+=("$path")
        PROJECT_TYPES+=("$type")
    done
    
    echo -e "${GREEN}✓ Found ${#PROJECTS_FOUND[@]} projects${NC}"
    echo ""
}

# Function to display project selection menu
show_menu() {
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  DeepAgents + Ollama - Project Picker"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    
    if [ ${#PROJECTS_FOUND[@]} -eq 0 ]; then
        echo -e "${RED}No projects found in $SCAN_DIR${NC}"
        echo ""
        echo "Projects are identified by:"
        echo "  - package.json (Node.js/JavaScript)"
        echo "  - pyproject.toml / requirements.txt (Python)"
        echo "  - Cargo.toml (Rust)"
        echo "  - go.mod (Go)"
        echo "  - .git directory"
        echo "  - .deepagents directory"
        exit 1
    fi
    
    echo "Available Projects:"
    echo ""
    
    local i=1
    for name in "${PROJECTS_FOUND[@]}"; do
        local path="${PROJECT_PATHS[$((i-1))]}"
        local type="${PROJECT_TYPES[$((i-1))]}"
        
        if [ -d "$path" ]; then
            echo -e "  ${GREEN}$i${NC}. ${CYAN}$name${NC}"
            echo -e "     Type: ${YELLOW}$type${NC}"
            echo "     Path: $path"
            echo ""
        else
            echo -e "  ${RED}$i${NC}. $name ${RED}(⚠️  Not found)${NC}"
            echo ""
        fi
        ((i++))
    done
    
    local cancel_option=${#PROJECTS_FOUND[@]}
    echo "  $((cancel_option + 1)). Cancel / Rescan"
    echo ""
    echo -n "Select a project (1-$((cancel_option + 1))): "
}

# Function to activate project
activate_project() {
    local project_name="$1"
    local project_path="$2"
    local project_type="$3"
    
    if [ ! -d "$project_path" ]; then
        echo -e "${RED}Error: Project path not found: $project_path${NC}"
        exit 1
    fi
    
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  Activating Project: $project_name"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo -e "  Name: ${CYAN}$project_name${NC}"
    echo -e "  Type: ${YELLOW}$project_type${NC}"
    echo "  Path: $project_path"
    echo ""
    
    # Create environment file for the selected project
    cat > "$SCRIPT_DIR/.project_env" << EOF
#!/bin/bash
# Auto-generated project environment
# Generated on: $(date)
export PROJECT_NAME="$project_name"
export PROJECT_PATH="$project_path"
export PROJECT_TYPE="$project_type"
export DEEP_AGENTS_PROJECT_ROOT="$project_path"
EOF
    
    echo -e "${GREEN}✓ Project activated!${NC}"
    echo ""
    echo "Environment saved to: $SCRIPT_DIR/.project_env"
    echo ""
    echo "Next steps:"
    echo "  1. Source environment: source $SCRIPT_DIR/.project_env"
    echo "  2. Navigate: cd \$PROJECT_PATH"
    echo "  3. Start agent: ./scripts/start-agent.sh"
    echo ""
}

# Function to show project details
show_project_details() {
    local idx=$1
    local name="${PROJECTS_FOUND[$idx]}"
    local path="${PROJECT_PATHS[$idx]}"
    local type="${PROJECT_TYPES[$idx]}"
    
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  Project Details: $name"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "  Name: $name"
    echo "  Type: $type"
    echo "  Path: $path"
    echo ""
    
    # Show additional details based on project type
    case "$type" in
        "Next.js"|"React"|"Vue.js"|"Angular"|"Node.js"|"Nuxt.js")
            if [ -f "$path/package.json" ]; then
                echo "  package.json:"
                echo "    Name: $(grep -m1 '"name"' "$path/package.json" | cut -d'"' -f4)"
                echo "    Version: $(grep -m1 '"version"' "$path/package.json" | cut -d'"' -f4)"
            fi
            ;;
        "FastAPI"|"Django"|"Flask"|"Python")
            if [ -f "$path/pyproject.toml" ]; then
                echo "  pyproject.toml found"
            elif [ -f "$path/requirements.txt" ]; then
                local req_count=$(wc -l < "$path/requirements.txt" 2>/dev/null || echo "0")
                echo "  requirements.txt: $req_count dependencies"
            fi
            ;;
    esac
    
    # Check for DeepAgents setup
    if [ -d "$path/.deepagents" ]; then
        echo ""
        echo -e "  ${GREEN}✓ DeepAgents configured${NC}"
        
        # List skills if available
        if [ -d "$path/.deepagents/skills" ]; then
            local skills=$(ls "$path/.deepagents/skills" 2>/dev/null | wc -l)
            echo "    Skills: $skills available"
        fi
        
        # Check for MCP config
        if [ -f "$path/.deepagents/.mcp.json" ]; then
            local mcp_count=$(grep -c '"mcpServers"' "$path/.deepagents/.mcp.json" 2>/dev/null || echo "0")
            echo "    MCP Servers: configured"
        fi
    fi
    
    # Check for git
    if [ -d "$path/.git" ]; then
        echo ""
        echo "  Git Repository:"
        cd "$path"
        local branch=$(git branch --show-current 2>/dev/null || echo "unknown")
        local status=$(git status --short 2>/dev/null | wc -l)
        echo "    Branch: $branch"
        echo "    Modified files: $status"
        cd - > /dev/null
    fi
    
    echo ""
}

# Main script
main() {
    # Parse arguments
    local rescan=false
    while [[ $# -gt 0 ]]; do
        case $1 in
            -r|--rescan)
                rescan=true
                shift
                ;;
            -h|--help)
                echo "Usage: $0 [OPTIONS]"
                echo ""
                echo "Options:"
                echo "  -r, --rescan    Force rescan for projects"
                echo "  -h, --help      Show this help message"
                echo ""
                echo "This script automatically scans $SCAN_DIR"
                echo "for software projects and allows interactive selection."
                exit 0
                ;;
            *)
                shift
                ;;
        esac
    done
    
    # Scan for projects
    scan_projects
    
    # Show menu
    show_menu
    read choice
    
    # Validate input
    if ! [[ "$choice" =~ ^[0-9]+$ ]]; then
        echo -e "${RED}Error: Please enter a number${NC}"
        exit 1
    fi
    
    local total_projects=${#PROJECTS_FOUND[@]}
    local cancel_option=$((total_projects + 1))
    
    if [ "$choice" -eq "$cancel_option" ]; then
        echo "Cancelled"
        exit 0
    fi
    
    if [ "$choice" -lt 1 ] || [ "$choice" -gt "$cancel_option" ]; then
        echo -e "${RED}Error: Invalid selection${NC}"
        exit 1
    fi
    
    # Get selected project
    local idx=$((choice - 1))
    local selected_name="${PROJECTS_FOUND[$idx]}"
    local selected_path="${PROJECT_PATHS[$idx]}"
    local selected_type="${PROJECT_TYPES[$idx]}"
    
    if [ -n "$selected_name" ]; then
        activate_project "$selected_name" "$selected_path" "$selected_type"
    else
        echo -e "${RED}Error: Invalid selection${NC}"
        exit 1
    fi
}

main "$@"
