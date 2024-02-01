run:install
	@echo "Running Flask Server"
	python3 -q app.py
install:
	@echo "Installing Dependencies"
	pip3 install -q -r requirement.txt
	@echo "Dependencies Installed"

