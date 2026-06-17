import os

vite_config_path = "frontend/vite.config.js"
with open(vite_config_path, "r") as f:
    vite_content = f.read()

new_vite_content = vite_content.replace(
    "plugins: [",
    "server: {\n    proxy: {\n      '/api': {\n        target: 'http://127.0.0.1:8000',\n        changeOrigin: true\n      }\n    }\n  },\n  plugins: ["
)

with open(vite_config_path, "w") as f:
    f.write(new_vite_content)

app_jsx_path = "frontend/src/App.jsx"
with open(app_jsx_path, "r") as f:
    app_content = f.read()

new_app_content = app_content.replace("http://localhost:8000/api", "/api")
new_app_content = new_app_content.replace("http://localhost:8000${endpoint}", "${endpoint}")

with open(app_jsx_path, "w") as f:
    f.write(new_app_content)

print("Fixed localhost URLs and updated Vite proxy!")
