import yaml
import sys

def load_yaml(file_path):
    """Load YAML file that may contain multiple documents."""
    with open(file_path, "r") as f:
        return list(yaml.safe_load_all(f))

def check_duplicate_labels(resources):
    """Check for duplicate labels within each resource."""
    errors = []
    for resource in resources:
        if not isinstance(resource, dict):  # Skip empty or malformed documents
            continue
        
        metadata = resource.get("metadata", {})
        labels = metadata.get("labels", {})

        if labels:
            seen = set()
            duplicates = [k for k in labels if k in seen or seen.add(k)]
            if duplicates:
                resource_name = metadata.get("name", "Unnamed")
                resource_kind = resource.get("kind", "Unknown")
                errors.append(f"Duplicate labels found in {resource_kind} '{resource_name}': {duplicates}")

    if errors:
        raise ValueError("\n".join(errors))  # Fail the pipeline with a proper error

    print("✅ No duplicate labels found.")

if __name__ == "__main__":
    yaml_file = "metrics-enabled-out.yml"  # Change this to your actual file path
    try:
        resources = load_yaml(yaml_file)
        check_duplicate_labels(resources)
    except ValueError as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)  # Explicitly fail the pipeline
