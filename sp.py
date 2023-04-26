import os

input_path = "audio/test"

# Split the path at each directory separator, regardless of platform
parts = []
while True:
    input_path, part = os.path.split(input_path)
    if part:
        parts.insert(0, part)
    else:
        if input_path:
            parts.insert(0, input_path)
        break

# Insert "output" between the first and second parts, and join the parts back together
output_path = os.path.join(parts[0], "output", *parts[1:])

print(output_path)  # audio/output/test