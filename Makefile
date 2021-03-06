# Update this to give whichever name you want. This may be set on the command line:
# > make build OUT_FILE=./outfile.zip
OUT_FILE?=./deliverable.zip

# get absolute path of zipfile to deliver
DELIVERABLE=$(abspath $(OUT_FILE))

FUNCTION_NAME?=investmentPortfolioBalancer

# Install all the libs locally
install:
	# pipenv --python 3.6
	pipenv install

# Destroy the virtualenv
uninstall:
	pipenv --rm

# Run the import
run:
	pipenv run python3.6 ./lambda_function.py

# Run the tests
.PHONY: test
test:
	pipenv run python3.6 -m test.calculator_test

# Clean delivrable
clean:
	rm -f ${DELIVERABLE}

# Rebuild the deliverable
build:
	$(eval VENV = $(shell pipenv --venv))
	cd ${VENV}/lib/python3.6/site-packages && zip -r9 ${DELIVERABLE} ./*
	zip -r9 ${DELIVERABLE} . -i '*.py'

# Update lambda function
update-lambda:
	aws lambda update-function-code --function-name ${FUNCTION_NAME} --zip-file fileb://${DELIVERABLE}

# Run python shell
pyshell:
	pipenv shell python3

# Run pipenv shell
virtualenv-shell:
	pipenv shell
