# PetClash
#### Video Demo:  https://youtu.be/V5H2J2pkO18
#### Description:

## Introduction
My final project for CS50x is a full-stack web application built with Python, Flask, and SQLAlchemy. The application serves as an interactive style voting platform for pets. Users can register accounts, securely upload photos of their own pets, and vote in head-to-head matchups to determine which pet is the cutest. The system automatically calculates and updates the global ranking of all pets using a complex mathematical ELO rating system.

Creating this project allowed me to combine multiple disciplines taught in CS50: database management using SQL (via an ORM), backend routing with Python, secure user authentication, and frontend responsive design using HTML, CSS, and Bootstrap.

## Design Choices and Technical Challenges

Throughout the development process, I faced several technical challenges that required specific architectural decisions. I chose not to take the easiest path in order to make the application more robust, fair, and secure.

### 1. The ELO Rating Algorithm vs. Simple Upvotes
The most significant design choice was how to handle the voting mechanism. Initially, I considered implementing a simple "like" counter or a win/loss ratio. However, I realized this would create a heavily skewed and unfair leaderboard. Pets that were uploaded on day one would naturally accumulate hundreds of votes, making it impossible for newly uploaded, potentially cuter pets to ever reach the top 20.

To solve this, I implemented the ELO rating system, widely used in competitive chess and video game matchmaking. Every pet starts with a baseline score of 1200. When two pets are matched, the system calculates the expected probability of winning for each. If a highly-rated pet defeats a low-rated pet, it gains very few points. But if an "underdog" wins, it steals a massive amount of points from the leader. I set the K-factor (maximum point fluctuation per vote) to 32. This choice ensures a dynamic, self-correcting, and strictly merit-based leaderboard.

### 2. Secure File Handling and Filename Collisions
Allowing users to upload files opens the server to significant vulnerabilities. My first approach was using Werkzeug's `secure_filename` to prevent Directory Traversal attacks (e.g., preventing a user from naming a file `../../../etc/passwd`).

However, this did not solve the issue of filename collisions. If User A uploads `cat.jpg` and User B also uploads `cat.jpg`, the server's operating system would overwrite the first image, corrupting the database references. To engineer around this, I imported Python's `uuid` library. Now, when a file is uploaded, the application completely discards the original filename. It splits the string to extract only the file extension (e.g., `.jpg`), generates a completely random, universally unique 128-bit identifier (UUID), and concatenates them. This completely eliminates the possibility of files overwriting each other.

### 3. Session Management and Flash Messages
During the implementation of the login system, I encountered a tricky bug involving Flask's `flash` messages and session clearing. Originally, I used `session.clear()` at the very beginning of the `/login` route to ensure the user was logged out before attempting to log in again. However, I discovered that Flask stores `flash` messages inside the session object itself. Consequently, `session.clear()` was instantly wiping out the error messages (like "Invalid password") before they could be rendered in the HTML template.

The architectural fix was to replace `session.clear()` with `session.pop("user_id", None)`. This precise targeting removes the user's authentication token while safely preserving the flash messages needed for the user interface.

### 4. Frontend Consistency with Object-Fit
On the frontend, handling user-generated content meant dealing with images of entirely different aspect ratios (some horizontal, some vertical). Relying solely on Bootstrap's grid system resulted in UI cards that jumped up and down in height, creating a poor user experience. I resolved this by applying fixed heights to the images combined with the CSS property `object-fit: cover`. This ensures every image perfectly fills its designated space without distorting or stretching the pet's proportions.

## File Manifest

* `app.py`: The core backend controller. It initializes the Flask application, configures the SQLite database via SQLAlchemy, defines the database models (`User` and `Pet`), and contains all the application routes, including the complex ELO calculation logic inside the `/vote` route.
* `pets.db`: The SQLite database containing all relational data.
* `requirements.txt`: The dependency file listing exactly what is needed to run the app (Flask, Flask-SQLAlchemy, and Werkzeug), completely stripped of unnecessary global packages.
* `templates/layout.html`: The foundational Jinja2 template containing the `head`, Bootstrap CDN links, the responsive navigation bar, and flash message rendering logic.
* `templates/index.html`: The main arena. It randomly selects two pets from the database and renders them as clickable form submission buttons.
* `templates/leaderboard.html`: A dynamically generated table displaying the top 20 pets sorted by their ELO score in descending order.
* `templates/add_image.html`: A secure form with `enctype="multipart/form-data"` enabling authenticated users to upload files.
* `templates/register.html` & `templates/login.html`: Standard user authentication interfaces.
* `static/uploads/`: The directory acting as the local storage bucket for all UUID-renamed image files.

This project was incredibly rewarding and represents the culmination of everything I've learned.
