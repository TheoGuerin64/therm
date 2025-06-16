# therm

## Supported Platforms

*Only tested platforms are considered supported.*

### Linux

- Fedora 42+

## Requirements

- [uv](https://docs.astral.sh/uv/getting-started/installation) (python package manager)

### Fedora

- `python3-dnf`
- `python3-libdnf5`

## Usage

1. **Clone the repository:**

    ```bash
    git clone https://github.com/TheoGuerin64/therm.git
    ```

2. **Change to the repository directory:**

    ```bash
    cd therm
    ```

3. **Install the general requirements:**

    ```bash
    uv sync --no-dev --frozen --no-cache
    ```

4. **Install distribution-specific requirements:**

    **For Fedora:**

    ```bash
    sudo dnf install -y python3-dnf python3-libdnf5
    ```

5. **Run the playbook:**

    ```bash
    ansible-playbook -i inventory.ini main.yml -K
    ```

6. **Remove the cloned repository:**

    ```bash
    cd ..
    rm -rf therm
    ```

7. **Log out and log back in or reboot your system:**
