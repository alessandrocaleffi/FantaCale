⚽ FantaCale Analyzer

Strategic decision support system for Serie A Fantasy Football managers.

FantaCale Analyzer is a Python-based Web Application designed to replace static spreadsheets with a dynamic, high-performance tool for player analysis, auction management, and seasonal monitoring.

📖 About The Project

Developed as part of the ICT ITS Piemonte Python Programming course (2024-2025), this tool addresses the two critical phases of a "Fantallenatore's" season:

The Auction: Enables split-second decisions through clear visualizations and instant sorting.

Season Management: Monitors player performance, identifies free agents, and tracks transfer targets.

Unlike standard lists, FantaCale allows you to cross-reference metrics (Average Rating, Price, Starting Status) to find the best value-for-money players using a custom Stack Sorting Algorithm.

✨ Key Features

⚡ Stack Logic Sorting: A cumulative sorting memory that allows multi-level organization (e.g., sort by "Team" first, then by "Average Rating" to see the best players per team).

🔍 Hybrid Filtering: * Quick Toolbar: One-click filters for "Penalty Takers", "Targets", or "Free Agents".

Advanced Search: Complex queries using logical operators (e.g., Price < 15 AND Stat > 6.5).

🎯 Live Target Management: Toggle "Target" status on players instantly via AJAX without reloading the page or losing your scroll position.

📊 Visual Insights:

Color-coded stats: Green/Blue badges for excellent stats.

Status alerts: Yellow highlights for targets, Red for injured/transferred players.

Budget Widget: Real-time calculation of remaining budget based on selected targets.

🛠️ Tech Stack

The project follows a simplified MVC (Model-View-Controller) architecture, prioritizing speed and low overhead.

Backend: Python 3.x, Flask

Database: SQLite3 (Raw SQL implementation without ORM for maximum query control and performance)

Frontend: Jinja2 Templating, Bootstrap 5 (Responsive), JavaScript (AJAX)

🚀 Getting Started

Prerequisites

Python 3.x installed

A db.txt (CSV format) file containing player data in the root directory.

Installation

Clone the repository

git clone [https://github.com/yourusername/fantacale-analyzer.git](https://github.com/yourusername/fantacale-analyzer.git)
cd fantacale-analyzer


Install dependencies

pip install flask


Run the application

python app.py


Access the Dashboard
Open your browser and navigate to:
http://127.0.0.1:5000

🧠 How It Works

The "Stack" Sorting

Unlike standard tables that forget your previous click, FantaCale remembers.

Action: Click Team, then click FantaAverage.

Result: The list is sorted by Average, but players with the same average remain sorted alphabetically by Team.

Data Import

The system automatically ingests the db.txt file upon startup, normalizing data (converting booleans and cleaning empty fields) to prevent SQL errors during sorting.

🔮 Future Improvements

Multi-user authentication system.

Integration with external APIs for live stat updates.

Advanced budget projection graphs.

👤 Author

Alessandro Caleffi Student @ ICT ITS Piemonte - Python Programming

Year: 2024-2025

Disclaimer: This project is for educational purposes and personal use for Fantasy Football leagues.
