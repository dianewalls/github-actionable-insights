# GitHub Actionable Insights 

This Streamlit web application provides insights into first-time contribution statistics for non-archived repositories in a GitHub organization.

## Features
- **First-Time PRs Opened vs. Merged Ratio**: Track how many first-time pull requests are opened and how many are successfully merged.
- **Response Time to First-Time PRs**: Measure the average response time to the first comment on a first-time contributor's PR.
- **First-Time Issues Opened vs. Closed**: Compare how many issues are opened by first-time users and how many get closed.
- **Second Contribution Tracking**: Identify how many first-time contributors make a second contribution within three months.

## Setup Instructions

### Prerequisites
- Python 3.8+
- A GitHub personal access token with `repo` permissions

### Installation
1. Clone the repository:
   ```sh
   git clone https://github.com/dianewalls/github-actionable-insights.git
   cd github-actionable-insights
   ```

2. Create a virtual environment and activate it:
   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```

4. Set up the `.env` file:
   - Copy `.env.sample` to `.env`
   - Replace `your_personal_github_token_here` with your actual GitHub token
   - Replace `your_github_org_name_here` with your GitHub organization name

### Running the App
Execute the following command to start the Streamlit app:
```sh
streamlit run app.py
```

## Usage
- Select a repository from the dropdown list.
- View metrics on first-time contributions and related statistics.

## Environment Variables
Ensure your `.env` file contains:
```
GITHUB_TOKEN=your_personal_github_token_here
GITHUB_ORG_NAME=your_github_org_name_here
```

## Dependencies
- `streamlit`
- `requests`
- `python-dotenv`
- `pandas`

## License
This project is licensed under the MIT License.

## Contributions
Contributions are welcome! Please feel free to open an issue or submit a pull request.

