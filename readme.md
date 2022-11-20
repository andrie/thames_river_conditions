# Thames River Condidions

This is an experimental project to use Python to create a single page website with paddling conditions on the River Thames, London, United Kingdom.

The project scrapes several websites from the UK environmental agency (for river leve warnings) as well as river closures.  In addition, it reads the API to extract the river flow rate as well as water level at various locks.

# Published results

The project runs once a day on Github Actions and renders at https://andrie.quarto.pub/river-thames-conditions-at-hampton-court/

# Requirements

To recreate this project, you need:

- Python 3.10.5
- Create a virtual environment using `python3 -m venv venv` and then restore the required libraries using `pip3 install -r requirements.txt`
- Quarto
- Jupyter notebooks

The project uses these Python libraries:

- Astral: to calculate sunrise, sunset, dawn and dusk times
- beautifulsoup: to scrape web pages
- pandas: for data manipulation
- plotly: for plotting
- itables: for data tables
- quarto: to create the results page in HTML format