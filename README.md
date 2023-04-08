# Stock-Finance-web-app
This project is a web application for a stock trading platform built using Flask, CS50's SQL module, and other helper functions. The application allows users to register for an account, log in and out, search for stock quotes, buy and sell stocks, and view transaction history.

# Getting Started
To run the application, open app.py. At the top of the file, there are several imports, including CS50's SQL module and a few helper functions. The file disables caching of responses and configures Jinja with a custom filter, usd, for formatting values as USD. It also configures Flask to store sessions on the local filesystem and sets up CS50's SQL module to use finance.db.

There are a variety of routes defined in the application. The login and logout routes are implemented and use db.execute to query finance.db. The login route uses check_password_hash to compare hashes of users' passwords, and login "remembers" that a user is logged in by storing his or her user_id in session. The logout route simply clears the session to log a user out.

Most routes are "decorated" with @login_required, a function defined in helpers.py. This decorator ensures that if a user tries to visit any of those routes, he or she will first be redirected to log in.

The helpers.py file includes several helper functions, including apology, which ultimately renders a template, apology.html. It also defines escape, which replaces special characters in apologies, and lookup, which given a stock symbol, returns a stock quote as a dictionary. The file also includes usd, a function that formats a float as USD.

The requirements.txt file lists the packages on which the application depends. In the static directory, you can find styles.css, where some initial CSS lives. In the templates directory, you can find login.html, apology.html, and layout.html.

# Specification
Register
Complete the implementation of register in such a way that it allows a user to register for an account via a form.

Require that a user input a username, implemented as a text field whose name is username. Render an apology if the user's input is blank or the username already exists.
Require that a user input a password, implemented as a text field whose name is password, and then that same password again, implemented as a text field whose name is confirmation. Render an apology if either input is blank or the passwords do not match.
Submit the user's input via POST to /register.
INSERT the new user into users, storing a hash of the user's password, not the password itself. Hash the user's password with generate_password_hash. You may want to create a new template (e.g., register.html) that's similar to login.html.
Quote
Complete the implementation of quote in such a way that it allows a user to look up a stock's current price.

Require that a user input a stock's symbol, implemented as a text field whose name is symbol.
Submit the user's input via POST to /quote.
Use the lookup function to find the stock's current price.
Render a template that displays the stock's name, symbol, and price.
License
This project is licensed under the MIT License - see the LICENSE file for details.
