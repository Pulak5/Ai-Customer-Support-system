from setuptools import setup, find_packages

setup(
    name="ai_ticket_system",
    version="0.1.0",
    description="Backend for the AI Customer Support Ticket System",
    author="Your Name",
    # This tells setuptools to look for the "app" folder and treat it as a package
    packages=find_packages(include=["app", "app.*"]),
    python_requires=">=3.11",
)