from flask import Flask, render_template, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)


def scrape_menu():
    url = "https://www.menicka.cz/772-restaurace-rio-club.html?t=jidelni-listek#m"
    headers = {
        "User-Agent":
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        " AppleWebKit/537.36 (KHTML, like Gecko)"
        " Chrome/114.0.0.0 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        return [{
            "category": "Error",
            "dish": f"Failed to fetch menu: {str(e)}"
        }]

    soup = BeautifulSoup(response.content, "html.parser")
    menu_block = soup.find("div", class_="menicka jl")

    if not menu_block:
        return [{
            "category": "Error",
            "dish": "Menu not found or site structure has changed."
        }]

    menu_items = []
    current_category = None

    for tag in menu_block.find_all(["div", "li"]):
        if "nadpis" in tag.get("class", []):
            current_category = tag.get_text(strip=True)
        elif "jidlo" in tag.get("class", []):
            dish = tag.get_text(strip=True)
            menu_items.append({"category": current_category, "dish": dish})

    if not menu_items:
        return [{
            "category": "Notice",
            "dish": "No menu items available today."
        }]

    return menu_items


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/get_menu")
def get_menu():
    menu = scrape_menu()
    return jsonify(menu)


if __name__ == "__main__":
    app.run()
