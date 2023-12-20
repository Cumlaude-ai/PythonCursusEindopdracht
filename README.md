# Interactive Dashboard Tool

This tool is a versatile dashboard for visualizing and exploring time-series data, utilizing Matplotlib, Dash, Plotly, Pandas, and other libraries. It provides interactive graphs and filtering functionalities to analyze data effectively.

## Usage

### Prerequisites

- Python 3.x
- Libraries: `dash`, `matplotlib`, `plotly`, `pandas`, `dash_bootstrap_components`, `dateutil`

### Installation

1. Clone this repository.
2. Install the required dependencies using `pip install -r requirements.txt`.

### Running the Dashboard

Run the `createDashboard()` function with appropriate parameters:

- `Title`: Title of the dashboard.
- `SiteUrl`: URL of the site.
- `LogoUrl`: URL of the logo image.
- `BackgroundUrl`: URL of the background image.
- `Graphs`: List of graphs or interactiveGraph objects to display.

```python
from datetime import datetime
# ... (import statements for libraries)

# (all the provided code)

# Example usage
Title = "Your Dashboard Title"
SiteUrl = "https://your-site-url.com"
LogoUrl = "https://your-logo-url.com/logo.png"
BackgroundUrl = "https://your-background-url.com/background.jpg"
graphs = []  # Add your graphs or interactiveGraph objects here

app = createDashboard(Title, SiteUrl, LogoUrl, BackgroundUrl, graphs)
```

Run the created `app` instance to launch the dashboard.

## Features

- **Interactive Graphs**: Visualize data with interactive graphs using Plotly and Matplotlib.
- **Filtering**: Filter data based on timeframes, percentages, and specific attributes using sliders and dropdowns.
- **Customization**: Easily configure and set up different interactive graphs with their respective filters.

## Contributions

Contributions and feature enhancements are welcome. Feel free to fork this repository, make changes, and create pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.

---

Feel free to add more sections or details as per your project's specific requirements and information.
