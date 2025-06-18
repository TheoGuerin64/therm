# therm

## Supported Platforms

*Only tested platforms are considered supported.*

### Linux

- Fedora 42+

## Usage

1. **Install uv:**

    ```bash
    curl -LsSf https://astral.sh/uv/install.sh | sh
    ```

2. **Install distribution-specific requirements:**

    **For Fedora:**

    ```bash
    sudo dnf install -y python3-dnf python3-libdnf5
    ```

3. **Clone the repository:**

    ```bash
    git clone https://github.com/TheoGuerin64/therm.git
    cd therm
    ```

4. **Run the playbook:**

    ```bash
    uv run --no-dev --frozen --no-cache ansible-playbook -i inventory.ini main.yml -K
    ```

5. **Remove the cloned repository:**

    ```bash
    cd ..
    rm -rf therm
    ```

6. **Log out and log back in or reboot your system**
