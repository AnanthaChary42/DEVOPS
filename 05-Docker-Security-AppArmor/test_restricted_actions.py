import docker

# Create a Docker client
client = docker.from_env()

# Run the container with the AppArmor profile
print("Starting container with AppArmor profile...")
container = client.containers.run(
    "flask-apparmor",
    name="flask-secure-test",
    ports={'5000/tcp': 5000},
    security_opt=["apparmor=my-apparmor-profile"],
    detach=True
)

print(f"Container started: {container.short_id}")

# Confirm the profile is actually attached before testing
info = client.api.inspect_container(container.id)
print(f"SecurityOpt: {info['HostConfig']['SecurityOpt']}")

# Test restricted actions
print("\n--- Testing Restricted Actions ---")

exit_code, output = container.exec_run("cat /etc/passwd")
print(f"Attempt to read /etc/passwd: Exit Code {exit_code}, Output: {output.decode().strip()}")

exit_code, output = container.exec_run("/bin/bash -c 'cat /etc/shadow'")
print(f"Attempt to execute /bin/bash: Exit Code {exit_code}, Output: {output.decode().strip()}")

# Stop and remove the container
print("\nStopping the container...")
container.stop()
container.remove()
print("Container stopped and removed.")
