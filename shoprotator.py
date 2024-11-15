import json
import os
import random
import requests
from datetime import datetime

def identify_category(cid):
    if cid and cid.startswith("CID_"):
        return "AthenaCharacter", cid
    elif cid and cid.startswith("BID_"):
        return "AthenaBackpack", cid
    elif cid and (cid.startswith("Pickaxe_ID_") or cid.startswith("Pickaxe_")):
        return "AthenaPickaxe", cid
    elif cid and cid.startswith("Glider_ID_"):
        return "AthenaGlider", cid
    elif cid and cid.startswith("EID_"):
        return "AthenaDance", cid
    else:
        return None, cid

def get_price(cid, rarity):
    price_mapping = {
        "AthenaCharacter": {
            "rare": 800,
            "super_rare": 1200,
            "epic": 1500,
            "legendary": 2000
        },
        "AthenaDance": {
            "rare": 200,
            "super_rare": 500,
            "epic": 800
        },
        "AthenaPickaxe": {
            "rare": 500,
            "super_rare": 800,
            "epic": 1200
        }
    }
    
    type, _ = identify_category(cid)
    return price_mapping.get(type, {}).get(rarity, random.randint(200, 2000))

def add_items(items_dict, rarity_mapping, backbling_mapping):
    items = {}
    for category, cid in items_dict.items():
        if cid is None:
            continue
        if isinstance(cid, dict):
            cid = cid['itemGrants'][0].split(":")[1]
        rarity = None
        for rarity_level, item_ids in rarity_mapping.items():
            if cid in item_ids:
                rarity = rarity_level
                break
        price = get_price(cid, rarity)
        type, full_type = identify_category(cid)
        if type:
            items[category] = {}
            if type == "AthenaCharacter" and rarity in ["super_rare", "epic", "legendary"] and cid in backbling_mapping:
                items[category]["itemGrants"] = [
                    f"{type}:{full_type}", 
                    f"AthenaBackpack:{backbling_mapping[cid]}"
                ]
            else:
                items[category]["itemGrants"] = [f"{type}:{full_type}"]
            items[category]["price"] = price
            items[category]["rarity"] = rarity
    return items

def save_to_file(shop):
    file_path = os.path.join(os.path.dirname(__file__), 'catalog_config.json')
    with open(file_path, 'w') as f:
        json.dump(shop, f, indent=4)
    print(f"\nConfiguration saved to {file_path}")

def get_random_item(rarity, category, used_items, combined_items):
    available_items = [item for item in combined_items[rarity] if identify_category(item)[0] == category and item not in used_items]
    if not available_items:
        return None
    selected_item = random.choice(available_items)
    used_items.add(selected_item)
    return selected_item

def ensure_non_none_items(num_items, category, used_items, combined_items):
    items = []
    retries = 0
    max_retries = 10
    while len(items) < num_items and retries < max_retries:
        item = get_random_item(random.choice(["rare", "super_rare", "epic", "legendary"]), category, used_items, combined_items)
        if item:
            items.append(item)
        retries += 1
    return items

def get_paired_featured_items(pairs, used_items, combined_items):
    available_pairs = [pair for pair in pairs if pair[0] not in used_items and pair[1] not in used_items]
    if not available_pairs:
        return None, None
    selected_pair = random.choice(available_pairs)
    used_items.update(selected_pair)
    return selected_pair

def send_to_discord(webhook_url, shop_data):
    date_str = datetime.now().strftime("%d/%m/%Y")
    
    def format_item(item):
        return item.split(":")[1] if ":" in item else item

    embed = {
        "author": {
            "name": f"ITEM SHOP {date_str}",
            "url": "",
        },
        "fields": [
            {"name": "featured 1", "value": format_item(shop_data.get('featured1', {}).get('itemGrants', [''])[0]), "inline": True},
            {"name": "featured 2", "value": format_item(shop_data.get('featured2', {}).get('itemGrants', [''])[0]), "inline": True},
            {"name": "daily 1", "value": format_item(shop_data.get('daily1', {}).get('itemGrants', [''])[0]), "inline": True},
            {"name": "daily 2", "value": format_item(shop_data.get('daily2', {}).get('itemGrants', [''])[0]), "inline": True},
            {"name": "daily 3", "value": format_item(shop_data.get('daily3', {}).get('itemGrants', [''])[0]), "inline": True},
            {"name": "daily 4", "value": format_item(shop_data.get('daily4', {}).get('itemGrants', [''])[0]), "inline": True},
            {"name": "daily 5", "value": format_item(shop_data.get('daily5', {}).get('itemGrants', [''])[0]), "inline": True},
            {"name": "daily 6", "value": format_item(shop_data.get('daily6', {}).get('itemGrants', [''])[0]), "inline": True},
        ],
        "image": {
            "url": "https://cdn.discordapp.com/attachments/12526c03916808a417a7336fc2350c328016be93daccc&"
        },
        "color": 0xffffff,
        "footer": {
            "text": "Item shop",
            "icon_url": "https://cdn.discordapp.com/attachments/12526c03916808a417a7336fc2350c328016be93daccc&"
        }
    }

    data = {
        "embeds": [embed]
    }

    response = requests.post(webhook_url, json=data)

    if response.status_code == 204:
        print("Message sent successfully")
    else:
        print(f"Failed to send message: {response.status_code}")

import requests

import requests

def generate_html(shop, featured_images):
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Izen Shop</title>
        <meta http-equiv="refresh" content="5"> <!-- Refresh every 5 seconds -->
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.3/css/all.min.css">
        <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@600&display=swap" rel="stylesheet">
        <link rel="icon" href="https://cdn.discordapp.com/attachments/1260286129639395461/1260635473437790311/Design_sem_nome_5.png?ex=669009c6&is=668eb846&hm=a694a0829b09b161f0e96f6cb23bb94432bff720c6d592bb40fa4f7fb8e8effd&" type="image/png">
        <style>
            body {
                font-family: 'Poppins', sans-serif;
                background: radial-gradient(circle at top, #111111, #000000);
                color: white;
                margin: 0;
                padding: 0;
                display: flex;
                justify-content: center;
                align-items: center;
                min-height: 100vh;
                overflow-x: hidden;
                position: relative;
            }

            body::before {
                content: '';
                position: absolute;
                top: 50%;
                left: 50%;
                width: 200%;
                height: 200%;
                background: radial-gradient(circle, rgba(255, 255, 255, 0.1), transparent 70%);
                transform: translate(-50%, -50%);
                pointer-events: none;
                filter: blur(100px);
            }

            .container {
                max-width: 1200px;
                margin: 0 auto;
                padding: 2rem;
                position: relative;
                z-index: 1;
            }

            .header {
                font-size: 1.75rem;
                font-weight: 700;
                display: flex;
                justify-content: center;
                align-items: center;
                margin-bottom: 2rem;
            }

            .header span {
                margin-left: 1rem;
                font-size: 1rem;
                color: #a0aec0;
            }

            #rotation-title {
                font-weight: bold;
                font-size: 30px;
                color: #ffffff;
                text-shadow: 0 0 10px rgba(255, 255, 255, 0.6);
            }

            .main-cards {
                display: flex;
                gap: 2rem;
                justify-content: space-between;
            }

            .card, .sub-card {
                background-color: #1c1c1e;
                padding: 1.5rem;
                border-radius: 20px;
                display: flex;
                flex-direction: column;
                align-items: center;
                box-shadow: 0 4px 15px rgba(0, 0, 0, 0.5);
                transition: transform 0.3s ease, background-color 0.3s ease;
            }

            .card:hover, .sub-card:hover {
                transform: translateY(-10px) scale(1.05);
                background-color: #28282b;
            }

            .card {
                flex: 1;
                margin: 0 1rem;
            }

            .card img {
                border-radius: 10px;
                width: 100%;
            }

            .card .text-lg {
                font-size: 1.25rem;
                text-align: center;
                margin-top: 1.5rem;
            }

            .price-tag {
                background: rgba(0, 0, 0, 0.8);
                padding: 0.75rem 1.5rem;
                border-radius: 12px;
                color: #fff;
                font-size: 1.125rem;
                text-align: center;
                margin-top: 0.75rem;
                display: flex;
                align-items: center;
                justify-content: center;
                font-weight: bold;
                box-shadow: 0 2px 5px rgba(0, 0, 0, 0.4);
            }

            .price-tag img {
                width: 1.25rem;
                height: 1.25rem;
                margin-left: 0.5rem;
            }

            .sub-cards-container {
                width: 100%;
                margin-top: 2rem;
            }

            .sub-cards {
                display: grid;
                grid-template-columns: repeat(3, 1fr);
                gap: 2rem;
            }

            .sub-card {
                padding: 1.5rem;
                border-radius: 16px;
            }

            .sub-card img {
                border-radius: 8px;
                width: 100%;
                margin-bottom: 1.5rem;
            }

            .sub-card .text-lg {
                font-size: 1.125rem;
                text-align: center;
            }

            #v-bucks {
                width: 24px;
                height: 20px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <span id="rotation-title" class="rotation-title">Current Rotation</span>
                <span class="rotation-date" id="date"></span>
            </div>
            <div class="main-cards">
    """

    def fetch_item_name(skin_id):
        url = f"https://fortnite-api.com/v2/cosmetics/br/{skin_id}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            return data["data"]["name"]
        else:
            return "Unknown"

    def generate_featured_item_html(item_data):
        item_grants = item_data['itemGrants'][0].split(":")[1]
        img_url = featured_images.get(item_grants, f"https://fortnite-api.com/images/cosmetics/br/{item_grants}/icon.png")
        item_name = fetch_item_name(item_grants)
        return f"""
        <div class="card">
            <img src="{img_url}" alt="{item_name}">
            <div class="text-lg">{item_name}</div>
            <div class="price-tag">{item_data['price']} V-Bucks <img src="images/v-bucks.png" id="v-bucks" alt="V-Bucks"></div>
        </div>
        """

    def generate_daily_item_html(item_data):
        item_grants = item_data['itemGrants'][0].split(":")[1]
        img_url = f"https://fortnite-api.com/images/cosmetics/br/{item_grants}/icon.png"
        item_name = fetch_item_name(item_grants)
        return f"""
        <div class="sub-card">
            <img src="{img_url}" alt="{item_name}">
            <div class="text-lg">{item_name}</div>
            <div class="price-tag">{item_data['price']} V-Bucks <img src="images/v-bucks.png" id="v-bucks" alt="V-Bucks"></div>
        </div>
        """

    # Generate HTML for featured items
    html_content += generate_featured_item_html(shop["featured1"])
    html_content += generate_featured_item_html(shop["featured2"])

    # Generate HTML for daily items
    html_content += """
                <div class="sub-cards-container">
                    <div class="sub-cards">
    """
    for category, data in shop.items():
        if category.startswith("daily"):
            html_content += generate_daily_item_html(data)

    html_content += """
                    </div>
                </div>
            </div>
        </div>
        <script>
            function formatDate(date) {
                const options = { year: 'numeric', month: 'long', day: 'numeric' };
                return date.toLocaleDateString(undefined, options);
            }

            const dateElement = document.getElementById('date');
            const currentDate = new Date();
            dateElement.textContent = formatDate(currentDate);

            function updateTime() {
                const now = new Date();
                const timeString = now.toLocaleTimeString();
                document.getElementById('current-time').innerText = timeString;
            }
            updateTime(); // Initial call to set the time immediately
            setInterval(updateTime, 1000); // Update the time every second
        </script>
    </body>
    </html>
    """

    with open("item_shop.html", "w") as file:
        file.write(html_content)
    print("HTML file generated: item_shop.html")

def main(include_battle_pass, include_exclusives, webhook_url, more_accurate=False):
    print("Starting script...")
    shop = {}
    current_season = 6

    # Define paired featured items
    paired_featured_items = {
        3: [
            ("CID_107_Athena_Commando_F_PajamaParty", "CID_093_Athena_Commando_M_Dinosaur"),
            ("CID_103_Athena_Commando_M_Bunny", "CID_104_Athena_Commando_F_Bunny"),
            ("CID_097_Athena_Commando_F_RockerPunk", "CID_268_Athena_Commando_M_RockerPunk")
        ],
        4: [
            ("CID_123_Athena_Commando_F_Metal", "CID_122_Athena_Commando_M_Metal"),
            ("CID_134_Athena_Commando_M_Jailbird", "CID_135_Athena_Commando_F_Jailbird"),
            ("CID_154_Athena_Commando_M_Gumshoe", "CID_155_Athena_Commando_F_Gumshoe"),
            ("CID_124_Athena_Commando_F_AuroraGlow", "CID_126_Athena_Commando_M_AuroraGlow")
        ],
        5: [
            ("CID_220_Athena_Commando_F_Clown", "CID_221_Athena_Commando_M_Clown"),
            ("CID_192_Athena_Commando_M_Hippie", "CID_193_Athena_Commando_F_Hippie"),
            ("CID_198_Athena_Commando_M_BlueSamurai", "CID_199_Athena_Commando_F_BlueSamurai")
        ],
        6: [
            ("CID_214_Athena_Commando_F_FootballReferee", "CID_215_Athena_Commando_M_FootballReferee"),
            ("CID_242_Athena_Commando_F_Bullseye", "CID_256_Athena_Commando_M_Pumpkin"),
            ("CID_255_Athena_Commando_F_HalloweenBunny", "CID_254_Athena_Commando_M_Zombie")
        ],
        7: [
            ("CID_328_Athena_Commando_F_Tennis", "CID_334_Athena_Commando_M_Scrapyard"),
            ("CID_297_Athena_Commando_F_Math", "CID_296_Athena_Commando_M_Math"),
            ("CID_345_Athena_Commando_M_LoveLlama", "EID_KissKiss")
        ],
        8: [
            ("CID_397_Athena_Commando_F_TreasureHunterFashion", "CID_398_Athena_Commando_M_TreasureHunterFashion"),
            ("CID_394_Athena_Commando_M_MoonlightAssassin", "CID_395_Athena_Commando_F_ShatterFly"),
            ("CID_372_Athena_Commando_F_Pirate01", "CID_373_Athena_Commando_M_Pirate01"),
            ("CID_358_Athena_Commando_M_Aztec", "CID_359_Athena_Commando_F_Aztec"),
            ("CID_355_Athena_Commando_M_Farmer", "CID_356_Athena_Commando_F_Farmer"),
            ("CID_392_Athena_Commando_F_BountyBunny", "CID_391_Athena_Commando_M_HoppityHeist")
        ]
    }

    skins_by_season = {
        1: {
            "rare": [
                "CID_041_Athena_Commando_F_District", "CID_040_Athena_Commando_M_District", 
                "CID_045_Athena_Commando_M_HolidaySweater", "CID_046_Athena_Commando_F_HolidaySweater", 
                "CID_016_Athena_Commando_F", "CID_013_Athena_Commando_F", "CID_014_Athena_Commando_F", 
                "CID_009_Athena_Commando_M", "CID_012_Athena_Commando_M", "CID_015_Athena_Commando_F", 
                "CID_011_Athena_Commando_M"
            ],
            "super_rare": [
                "CID_037_Athena_Commando_F_WinterCamo", "CID_042_Athena_Commando_M_Cyberpunk", 
                "CID_047_Athena_Commando_F_HolidayReindeer", "CID_051_Athena_Commando_M_HolidayElf", 
                "CID_044_Athena_Commando_F_SciPop", "CID_024_Athena_Commando_F", "CID_019_Athena_Commando_M", 
                "CID_023_Athena_Commando_F", "CID_026_Athena_Commando_M", "CID_027_Athena_Commando_F", 
                "CID_018_Athena_Commando_M", "CID_021_Athena_Commando_F", "CID_020_Athena_Commando_M", 
                "CID_022_Athena_Commando_F", "CID_025_Athena_Commando_M", "CID_028_Athena_Commando_F", 
                "CID_017_Athena_Commando_M"
            ],
            "epic": [
                "CID_038_Athena_Commando_M_Disco", "CID_048_Athena_Commando_F_HolidayGingerbread", 
                "CID_049_Athena_Commando_M_HolidayGingerbread", "CID_029_Athena_Commando_F_Halloween", 
                "CID_030_Athena_Commando_M_Halloween"
            ],
            "legendary": [
                "CID_031_Athena_Commando_M_Retro", "CID_050_Athena_Commando_M_HolidayNutcracker",
                "CID_034_Athena_Commando_F_Medieval"
            ]
        },
        2: {
            "rare": [
                "CID_079_Athena_Commando_F_Camo", "CID_074_Athena_Commando_F_Stripe", 
                "CID_075_Athena_Commando_F_Stripe", "CID_078_Athena_Commando_M_Camo",
                "CID_106_Athena_Commando_F_Taxi", "CID_098_Athena_Commando_F_StPatty", 
                "CID_086_Athena_Commando_M_RedSilk", "CID_087_Athena_Commando_F_RedSilk"
            ],
            "super_rare": [
                "CID_074_Athena_Commando_F_Stripe", "CID_072_Athena_Commando_M_Scout", 
                "CID_076_Athena_Commando_F_Sup", "CID_073_Athena_Commando_F_Scuba", 
                "CID_077_Athena_Commando_M_Sup", "CID_110_Athena_Commando_F_CircuitBreaker", 
                "CID_101_Athena_Commando_M_Stealth", "CID_092_Athena_Commando_F_RedShirt", 
                "CID_091_Athena_Commando_M_RedShirt"
            ],
            "epic": [
                "CID_061_Athena_Commando_F_SkiGirl", "CID_067_Athena_Commando_F_SkiGirl_CHN",
                "CID_066_Athena_Commando_F_SkiGirl_GER", "CID_065_Athena_Commando_F_SkiGirl_FRA",
                "CID_064_Athena_Commando_F_SkiGirl_GBR", "CID_063_Athena_Commando_F_SkiGirl_CAN",
                "CID_062_Athena_Commando_F_SkiGirl_USA", "CID_061_Athena_Commando_F_SkiGirl",
                "CID_060_Athena_Commando_M_SkiDude_KOR", "CID_059_Athena_Commando_M_SkiDude_CHN",
                "CID_058_Athena_Commando_M_SkiDude_GER", "CID_057_Athena_Commando_M_SkiDude_FRA",
                "CID_056_Athena_Commando_M_SkiDude_GBR", "CID_055_Athena_Commando_M_SkiDude_CAN",
                "CID_054_Athena_Commando_M_SkiDude_USA", "CID_053_Athena_Commando_M_SkiDude",
                "CID_112_Athena_Commando_M_Brite", "CID_111_Athena_Commando_F_Robo",
                "CID_109_Athena_Commando_M_Pizza", "CID_103_Athena_Commando_M_Bunny",
                "CID_104_Athena_Commando_F_Bunny", "CID_099_Athena_Commando_F_Scathach",
                "CID_094_Athena_Commando_M_Rider"
            ],
            "legendary": [
                "CID_071_Athena_Commando_M_Wukong", "CID_070_Athena_Commando_M_Cupid",
                "CID_069_Athena_Commando_F_PinkBear", "CID_107_Athena_Commando_F_PajamaParty",
                "CID_093_Athena_Commando_M_Dinosaur", "CID_105_Athena_Commando_F_SpaceBlack",
                "CID_102_Athena_Commando_M_Raven", "CID_097_Athena_Commando_F_RockerPunk",
                "CID_100_Athena_Commando_M_CuChulainn"
            ]
        },
        3: {
            "rare": [
                
            ],
            "super_rare": [
                "CID_268_Athena_Commando_M_RockerPunk",   
            ],
            "epic": [
                "CID_103_Athena_Commando_M_Bunny", "CID_104_Athena_Commando_F_Bunny",
            ],
            "legendary": [
                "CID_097_Athena_Commando_F_RockerPunk", "CID_268_Athena_Commando_M_RockerPunk",
            ]
        },
        4: {
            "rare": [
                "CID_124_Athena_Commando_F_AuroraGlow", "CID_126_Athena_Commando_M_AuroraGlow",
            ],
            "super_rare": [
                "CID_260_Athena_Commando_F_StreetOps", "CID_259_Athena_Commando_M_StreetOps",
                "CID_275_Athena_Commando_M_SniperHood", "CID_276_Athena_Commando_F_SniperHood",
                "CID_268_Athena_Commando_M_RockerPunk", "CID_271_Athena_Commando_F_SushiChef",
                "CID_191_Athena_Commando_M_SushiChef", "CID_262_Athena_Commando_M_MadCommander",
                "CID_263_Athena_Commando_F_MadCommander", "CID_246_Athena_Commando_F_Grave",
                "CID_223_Athena_Commando_M_Dieselpunk", "CID_223_Athena_Commando_M_Dieselpunk","CID_122_Athena_Commando_M_Metal","CID_123_Athena_Commando_F_Metal"
            ],
            "epic": [
                "CID_220_Athena_Commando_F_Clown", "CID_221_Athena_Commando_M_Clown ",
                "CID_192_Athena_Commando_M_Hippie ", "CID_193_Athena_Commando_F_Hippie",
            ],
            "legendary": [
                "CID_198_Athena_Commando_M_BlueSamurai", "CID_199_Athena_Commando_F_BlueSamurai",
            ]
        },
        6: {
            "rare": [
                "CID_214_Athena_Commando_F_FootballReferee", "CID_215_Athena_Commando_M_FootballReferee",
                "CID_242_Athena_Commando_F_Bullseye", "CID_256_Athena_Commando_M_Pumpkin",
                "CID_255_Athena_Commando_F_HalloweenBunny", "CID_254_Athena_Commando_M_Zombie"
            ],
            "super_rare": [
                "CID_260_Athena_Commando_F_StreetOps", "CID_259_Athena_Commando_M_StreetOps",
                "CID_275_Athena_Commando_M_SniperHood", "CID_276_Athena_Commando_F_SniperHood",
                "CID_268_Athena_Commando_M_RockerPunk", "CID_271_Athena_Commando_F_SushiChef",
                "CID_191_Athena_Commando_M_SushiChef", "CID_262_Athena_Commando_M_MadCommander",
                "CID_263_Athena_Commando_F_MadCommander", "CID_246_Athena_Commando_F_Grave",
                "CID_223_Athena_Commando_M_Dieselpunk", "CID_223_Athena_Commando_M_Dieselpunk"
            ],
            "epic": [
                "CID_247_Athena_Commando_M_GuanYu", "CID_277_Athena_Commando_M_Moth",
                "CID_272_Athena_Commando_M_HornedMask", "CID_274_Athena_Commando_M_Feathers",
                "CID_269_Athena_Commando_M_Wizard", "CID_270_Athena_Commando_F_Witch",
                "CID_266_Athena_Commando_F_LlamaRider", "CID_264_Athena_Commando_M_AnimalJackets",
                "CID_265_Athena_Commando_F_AnimalJackets", "CID_251_Athena_Commando_F_Muertos",
                "CID_252_Athena_Commando_M_Muertos", "CID_258_Athena_Commando_F_FuzzyBearHalloween",
                "CID_244_Athena_Commando_M_PumpkinSuit", "CID_228_Athena_Commando_M_Vampire",
                "CID_243_Athena_Commando_M_PumpkinSlice", "CID_240_Athena_Commando_F_Plague",
                "CID_241_Athena_Commando_M_Plague", "CID_235_Athena_Commando_M_Scarecrow",
                "CID_225_Athena_Commando_M_Octoberfest", "CID_226_Athena_Commando_F_Octoberfest","CID_220_Athena_Commando_F_Clown","CID_192_Athena_Commando_M_Hippie","CID_221_Athena_Commando_M_Clown","CID_154_Athena_Commando_M_Gumshoe","CID_155_Athena_Commando_F_Gumshoe"
            ],
            "legendary": [
                "CID_257_Athena_Commando_M_SamuraiUltra", "CID_250_Athena_Commando_M_EvilCowboy",
                "CID_248_Athena_Commando_M_BlackWidow", "CID_249_Athena_Commando_F_BlackWidow"
            ]
        },
        7: {
            "rare": [
                
            ],
            "super_rare": [
                "CID_328_Athena_Commando_F_Tennis", "CID_334_Athena_Commando_M_Scrapyard",
                "CID_297_Athena_Commando_F_Math", "CID_296_Athena_Commando_M_Math",
                "CID_345_Athena_Commando_M_LoveLlama","CID_328_Athena_Commando_F_Tennis","CID_334_Athena_Commando_M_Scrapyard"
            ],
            "epic": [
                
            ],
            "legendary": [
                
            ]
        },
        8: {
            "rare": [
                "CID_397_Athena_Commando_F_TreasureHunterFashion", "CID_398_Athena_Commando_M_TreasureHunterFashion",
                "CID_401_Athena_Commando_M_Miner", "CID_392_Athena_Commando_F_BountyBunny", 
                "CID_387_Athena_Commando_F_Golf", "CID_383_Athena_Commando_F_Cacti", 
                "CID_354_Athena_Commando_M_MunitionsExpert", "CID_355_Athena_Commando_M_Farmer",
                "CID_356_Athena_Commando_F_Farmer"
            ],
            "super_rare": [
                "CID_395_Athena_Commando_F_ShatterFly", "CID_391_Athena_Commando_M_HoppityHeist",
                "CID_372_Athena_Commando_F_Pirate01", "CID_373_Athena_Commando_M_Pirate01",
                "CID_381_Athena_Commando_F_BaseballKitbash", "CID_382_Athena_Commando_M_BaseballKitbash",
                "CID_363_Athena_Commando_M_SciOps", "CID_364_Athena_Commando_F_SciOps",
                "CID_366_Athena_Commando_M_Tropical", "CID_353_Athena_Commando_F_Bandolier",
                "CID_358_Athena_Commando_M_Aztec", "CID_359_Athena_Commando_F_Aztec",
                "CID_357_Athena_Commando_M_OrangeCamo"
            ],
            "epic": [
                "CID_394_Athena_Commando_M_MoonlightAssassin", "CID_396_Athena_Commando_F_Swashbuckler",
                "CID_393_Athena_Commando_M_Shiny", "CID_388_Athena_Commando_M_TheBomb",
                "CID_390_Athena_Commando_M_EvilBunny", "CID_376_Athena_Commando_M_DarkShaman",
                "CID_377_Athena_Commando_F_DarkShaman", "CID_301_Athena_Commando_M_Rhino",
                "CID_365_Athena_Commando_M_LuckyRider", "CID_361_Athena_Commando_M_BandageNinja",
                "CID_362_Athena_Commando_F_BandageNinja","CID_358_Athena_Commando_M_Aztec","CID_359_Athena_Commando_F_Aztec"
            ],
            "legendary": [
                "CID_385_Athena_Commando_M_PilotSkull", "CID_369_Athena_Commando_F_DevilRock"
            ]
        }
    }
    
    skins_battlepass_by_season = {
        2: {
            "legendary": ["CID_084_Athena_Commando_M_Assassin", "CID_088_Athena_Commando_M_SpaceBlack"],
            "epic": [
                "CID_080_Athena_Commando_M_Space", "CID_081_Athena_Commando_F_Space",
                "CID_082_Athena_Commando_M_Scavenger", "CID_083_Athena_Commando_F_Tactical"
            ],
            "super_rare": ["Pickaxe_ID_027_Scavenger"],
            "rare": ["EID_Salute"],
            "super_rare": ["EID_TakeTheL", "EID_BestMates"],
            "epic": ["EID_Robot"]
        },
        6: {
            "legendary": [
                "CID_230_Athena_Commando_M_Werewolf", "CID_237_Athena_Commando_F_Cowgirl",
                "CID_267_Athena_Commando_M_RobotRed"
            ],
            "epic": [
                "CID_227_Athena_Commando_F_Vampire", "CID_231_Athena_Commando_F_RedRiding",
                "CID_232_Athena_Commando_F_HalloweenTomato", "CID_233_Athena_Commando_M_FortniteDJ",
                "CID_234_Athena_Commando_M_LlamaRider"
            ],
            "super_rare": [
                "EID_Octopus", "EID_RunningMan", "EID_NeedToGo"
            ],
            "rare": [
                "EID_RegalWave"
            ]
        },
        8: {
            "legendary": ["CID_378_Athena_Commando_M_FurnaceFace", "CID_346_Athena_Commando_M_DragonNinja",
                          "CID_347_Athena_Commando_M_PirateProgressive", "CID_352_Athena_Commando_F_Shiny"],
            "epic": [
                "CID_348_Athena_Commando_F_Medusa", "CID_349_Athena_Commando_M_Banana",
                "CID_350_Athena_Commando_M_MasterKey", "CID_351_Athena_Commando_F_FireElf"
            ],
            "super_rare": ["Pickaxe_ID_167_Medusa", "Pickaxe_ID_165_MasterKey"],
            "rare": ["EID_HappyWave"],
            "super_rare": ["EID_YouBoreMe", "EID_Banana", "EID_Conga"],
            "epic": ["EID_HulaHoop"]
        }
    }

    exclusive_items = {
        "rare": [],
        "super_rare": ["Pickaxe_ID_039_TacticalBlack"],
        "epic": [
            "CID_090_Athena_Commando_M_Tactical", "CID_085_Athena_Commando_M_Twitch"
        ],
        "legendary": [
            "CID_095_Athena_Commando_M_Founder", "CID_089_Athena_Commando_M_RetroGrey",
            "CID_096_Athena_Commando_F_Founder"
        ]
    }

    backbling_mapping = {
        "CID_038_Athena_Commando_M_Disco": "BID_323_FunkOpsRemix",
        "CID_048_Athena_Commando_F_HolidayGingerbread": "BID_187_GingerbreadFemale",
        "CID_049_Athena_Commando_M_HolidayGingerbread": "BID_186_GingerbreadMale",
        "CID_050_Athena_Commando_M_HolidayNutcracker": "BID_182_NutcrackerMale",
        "CID_034_Athena_Commando_F_Medieval": "BID_003_RedKnight",
        "CID_035_Athena_Commando_M_Medieval": "BID_004_BlackKnight",
        "CID_032_Athena_Commando_M_Medieval": "BID_001_BlueSquire",
        "CID_033_Athena_Commando_F_Medieval": "BID_002_RoyaleKnight",
        "CID_061_Athena_Commando_F_SkiGirl": "BID_014_SkiGirl",
        "CID_067_Athena_Commando_F_SkiGirl_CHN": "BID_020_SkiGirl_CHN",
        "CID_066_Athena_Commando_F_SkiGirl_GER": "BID_019_SkiGirl_GER",
        "CID_065_Athena_Commando_F_SkiGirl_FRA": "BID_021_SkiGirl_FRA",
        "CID_064_Athena_Commando_F_SkiGirl_GBR": "BID_017_SkiGirl_GBR",
        "CID_063_Athena_Commando_F_SkiGirl_CAN": "BID_016_SkiGirl_CAN",
        "CID_062_Athena_Commando_F_SkiGirl_USA": "BID_015_SkiGirl_USA",
        "CID_060_Athena_Commando_M_SkiDude_KOR": "BID_013_SkiDude_KOR",
        "CID_059_Athena_Commando_M_SkiDude_CHN": "BID_012_SkiDude_CHN",
        "CID_058_Athena_Commando_M_SkiDude_GER": "BID_011_SkiDude_GER",
        "CID_057_Athena_Commando_M_SkiDude_FRA": "BID_010_SkiDude_FRA",
        "CID_056_Athena_Commando_M_SkiDude_GBR": "BID_009_SkiDude_GBR",
        "CID_055_Athena_Commando_M_SkiDude_CAN": "BID_008_SkiDude_CAN",
        "CID_054_Athena_Commando_M_SkiDude_USA": "BID_007_SkiDude_USA",
        "CID_053_Athena_Commando_M_SkiDude": "BID_014_SkiGirl",
        "CID_071_Athena_Commando_M_Wukong": "BID_182_NutcrackerMale",
        "CID_070_Athena_Commando_M_Cupid": "BID_022_Cupid",
        "CID_112_Athena_Commando_M_Brite": "BID_026_Brite",
        "CID_109_Athena_Commando_M_Pizza": "BID_043_Pizza",
        "CID_103_Athena_Commando_M_Bunny": "BID_037_BunnyMale",
        "CID_104_Athena_Commando_F_Bunny": "BID_038_BunnyFemale",
        "CID_099_Athena_Commando_F_Scathach": "BID_035_Scathach",
        "CID_094_Athena_Commando_M_Rider": "BID_381_RustyRaiderMotor",
        "CID_107_Athena_Commando_F_PajamaParty": "BID_041_PajamaParty",
        "CID_093_Athena_Commando_M_Dinosaur": "BID_031_Dinosaur",
        "CID_105_Athena_Commando_F_SpaceBlack": "BID_039_SpaceBlackFemale",
        "CID_102_Athena_Commando_M_Raven": "BID_036_Raven",
        "CID_097_Athena_Commando_F_RockerPunk": "BID_034_RockerPunk",
        "CID_100_Athena_Commando_M_CuChulainn": "BID_063_CuChulainn",
        "CID_082_Athena_Commando_M_Scavenger": "BID_027_Scavenger",
        "CID_083_Athena_Commando_F_Tactical": "BID_025_Tactical",
        "CID_088_Athena_Commando_M_SpaceBlack": "BID_028_SpaceBlack",
        "CID_090_Athena_Commando_M_Tactical": "BID_030_TacticalRogue",
        "CID_095_Athena_Commando_M_Founder": "BID_032_FounderMale",
        "CID_096_Athena_Commando_F_Founder": "BID_033_FounderFemale",
        "CID_260_Athena_Commando_F_StreetOps": "BID_141_StreetOpsFemale",
        "CID_259_Athena_Commando_M_StreetOps": "BID_140_StreetOpsMale",
        "CID_275_Athena_Commando_M_SniperHood": "BID_155_SniperHoodMale",
        "CID_271_Athena_Commando_F_SushiChef": "BID_151_SushiChefFemale",
        "CID_191_Athena_Commando_M_SushiChef": "BID_088_SushiChefMale",
        "CID_262_Athena_Commando_M_MadCommander": "BID_143_MadCommanderMale",
        "CID_263_Athena_Commando_F_MadCommander": "BID_144_MadCommanderFemale",
        "CID_223_Athena_Commando_M_Dieselpunk": "BID_116_DieselpunkFemale",
        "CID_223_Athena_Commando_M_Dieselpunk": "BID_115_DieselpunkMale",
        "CID_247_Athena_Commando_M_GuanYu": "BID_133_GuanYu",
        "CID_277_Athena_Commando_M_Moth": "BID_157_MothMale",
        "CID_272_Athena_Commando_M_HornedMask": "BID_153_HornedMaskFemale",
        "CID_274_Athena_Commando_M_Feathers": "BID_154_Feathers",
        "CID_269_Athena_Commando_M_Wizard": "BID_149_Wizard",
        "CID_270_Athena_Commando_F_Witch": "BID_150_Witch",
        "CID_264_Athena_Commando_M_AnimalJackets": "BID_145_AnimalJacketsMale",
        "CID_265_Athena_Commando_F_AnimalJackets": "BID_146_AnimalJacketsFemale",
        "CID_251_Athena_Commando_F_Muertos": "BID_135_MuertosFemale",
        "CID_252_Athena_Commando_M_Muertos": "BID_136_MuertosMale",
        "CID_228_Athena_Commando_M_Vampire": "BID_130_VampireMale02",
        "CID_243_Athena_Commando_M_PumpkinSlice": "BID_129_PumpkinSlice",
        "CID_240_Athena_Commando_F_Plague": "BID_128_PlagueFemale",
        "CID_241_Athena_Commando_M_Plague": "BID_127_PlagueMale",
        "CID_235_Athena_Commando_M_Scarecrow": "BID_124_ScarecrowMale",
        "CID_225_Athena_Commando_M_Octoberfest": "BID_117_OctoberfestMale",
        "CID_226_Athena_Commando_F_Octoberfest": "BID_118_OctoberfestFemale",
        "CID_257_Athena_Commando_M_SamuraiUltra": "BID_142_SamuraiUltra",
        "CID_250_Athena_Commando_M_EvilCowboy": "BID_137_EvilCowboy",
        "CID_248_Athena_Commando_M_BlackWidow": "BID_132_BlackWidowMale",
        "CID_249_Athena_Commando_F_BlackWidow": "BID_131_BlackWidowfemale",
        "CID_230_Athena_Commando_M_Werewolf": "BID_120_Werewolf",
        "CID_267_Athena_Commando_M_RobotRed": "BID_148_RobotRed",
        "CID_395_Athena_Commando_F_ShatterFly": "BID_256_ShatterFly",
        "CID_391_Athena_Commando_M_HoppityHeist": "BID_253_HoppityHeist",
        "CID_372_Athena_Commando_F_Pirate01": "BID_236_Pirate01Female",
        "CID_373_Athena_Commando_M_Pirate01": "BID_238_Pirate02Male",
        "CID_381_Athena_Commando_F_BaseballKitbash": "BID_245_BaseballKitbashFemale",
        "CID_382_Athena_Commando_M_BaseballKitbash": "BID_246_BaseballKitbashMale",
        "CID_363_Athena_Commando_M_SciOps": "BID_228_SciOpsMale",
        "CID_364_Athena_Commando_F_SciOps": "BID_227_SciOpsFemale",
        "CID_366_Athena_Commando_M_Tropical": "BID_230_TropicalMale",
        "CID_358_Athena_Commando_M_Aztec": "BID_221_AztecMale",
        "CID_359_Athena_Commando_F_Aztec": "BID_222_AztecFemale",
        "CID_357_Athena_Commando_M_OrangeCamo": "BID_223_OrangeCamo",
        "CID_394_Athena_Commando_M_MoonlightAssassin": "BID_255_MoonlightAssassin",
        "CID_396_Athena_Commando_F_Swashbuckler": "BID_257_Swashbuckler",
        "CID_393_Athena_Commando_M_Shiny": "BID_254_ShinyMale",
        "CID_388_Athena_Commando_M_TheBomb": "BID_250_TheBomb",
        "CID_390_Athena_Commando_M_EvilBunny": "BID_252_EvilBunny",
        "CID_376_Athena_Commando_M_DarkShaman": "BID_240_DarkShamanMale",
        "CID_377_Athena_Commando_F_DarkShaman": "BID_241_DarkShamanFemale",
        "CID_301_Athena_Commando_M_Rhino": "BID_171_Rhino",
        "CID_365_Athena_Commando_M_LuckyRider": "BID_229_LuckyRiderMale",
        "CID_361_Athena_Commando_M_BandageNinja": "BID_452_BandageNinjaBlue",
        "CID_362_Athena_Commando_F_BandageNinja": "BID_226_BandageNinjaFemale",
        "CID_378_Athena_Commando_M_FurnaceFace": "BID_242_FurnaceFace",
        "CID_346_Athena_Commando_M_DragonNinja": "BID_216_PirateProgressive",
        "CID_352_Athena_Commando_F_Shiny": "BID_217_ShinyFemale",
        "CID_107_Athena_Commando_F_PajamaParty": "BID_041_PajamaParty",
        "CID_093_Athena_Commando_M_Dinosaur": "BID_031_Dinosaur",
        "CID_103_Athena_Commando_M_Bunny": "BID_037_BunnyMale",
        "CID_104_Athena_Commando_F_Bunny ": "BID_038_BunnyFemale",
        "CID_097_Athena_Commando_F_RockerPunk": "BID_034_RockerPunk",
        "CID_134_Athena_Commando_M_Jailbird": "BID_053_JailbirdMale",
        "CID_135_Athena_Commando_F_Jailbird": "BID_054_JailbirdFemale",
        "CID_154_Athena_Commando_M_Gumshoe": "BID_062_Gumshoe",
        "CID_155_Athena_Commando_F_Gumshoe": "BID_067_GumshoeFemale",
        "CID_220_Athena_Commando_F_Clown": "BID_111_ClownFemale",
        "CID_221_Athena_Commando_M_Clown ": "BID_112_ClownMale",
        "CID_192_Athena_Commando_M_Hippie": "BID_093_HippieMale",
        "CID_193_Athena_Commando_F_Hippie ": "BID_094_HippieFemale",
        "CID_198_Athena_Commando_M_BlueSamurai": "BID_098_BlueSamuraiMale",
        "CID_199_Athena_Commando_F_BlueSamurai": "BID_099_BlueSamuraiFemale",
        "CID_328_Athena_Commando_F_Tennis": "BID_206_ScrapyardFemale",
        "CID_334_Athena_Commando_M_Scrapyard": "BID_205_ScrapyardMale",
        "CID_297_Athena_Commando_F_Math": "BID_170_MathFemale",
        "CID_296_Athena_Commando_M_Math": "BID_169_MathMale",
        "CID_345_Athena_Commando_M_LoveLlama": "BID_214_LoveLlama"

        
        
        
    }

    emotes_by_season = {
        1: {
            "rare": ["EID_FingerGuns", "EID_SlowClap"],
            "super_rare": ["EID_Dab"],
            "epic": ["EID_Fresh"]
        },
        2: {
            "rare": ["EID_TrueLove", "EID_Flex", "EID_HeelClick", "EID_RockPaperScissors", 
                     "EID_Celebration", "EID_DustOffShoulders", "EID_BreakYou", "EID_Facepalm"],
            "super_rare": ["EID_KissKiss", "EID_PureSalt", "EID_Flapper", "EID_Tidy", 
                           "EID_Confused", "EID_Wiggle", "EID_TapShuffle", "EID_IrishJig", 
                           "EID_MakeItRain", "EID_SexyFlip"],
            "epic": ["EID_EasternBloc", "EID_RockGuitar", "EID_DiscoFever", "EID_RocketRodeo", 
                     "EID_Zombie", "EID_BreakDance"]
        },
        6: {
            "rare": [
                "EID_TimeOut", "EID_ScoreCard", "EID_Disagree", "EID_WolfHowl",
                "EID_LookAtThis", "EID_TPose"
            ],
            "super_rare": [
                "EID_CowboyDance", "EID_Showstopper", "EID_Mime", "EID_AfroHouse",
                "EID_CrazyFeet", "EID_TaiChi", "EID_Touchdown", "EID_Texting",
                "EID_CrissCross", "EID_Juggler", "EID_HalloweenCandy", "EID_HeadBang",
                "EID_ElectroSwing", "EID_Sprinkler", "EID_SomethingStinks"
            ],
            "epic": [
                "EID_Saxophone", "EID_Wizard", "EID_DJ01", "EID_KPopDance02"
            ]
        },
        8: {
            "rare": ["EID_JazzHands", "EID_MartialArts", "EID_Shadowboxing", "EID_WackyWavy"],
            "super_rare": [
                "EID_IndianDance", "EID_Bunnyhop", "EID_Breakboy", "EID_DreamFeet",
                "EID_FancyWorkout", "EID_TimetravelBackflip", "EID_DrumMajor",
                "EID_ThighSlapper", "EID_MakeItRainV2", "EID_Floppy", "EID_Spyglass"
            ],
            "epic": ["EID_FireDance"]
        }
    }

    pickaxes_by_season = {
        1: {
            "rare": ["Pickaxe_ID_014_WinterCamo", "Pickaxe_ID_022_HolidayGiftWrap"],
            "super_rare": ["Pickaxe_ID_021_Megalodon", "Pickaxe_ID_020_Keg"],
            "epic": [
                "Pickaxe_ID_017_Shark", "Pickaxe_ID_018_Anchor", 
                "Pickaxe_ID_016_Disco", "Pickaxe_ID_015_HolidayCandyCane",
                "Pickaxe_Flamingo", "Pickaxe_Deathvalley", "Pickaxe_Lockjaw"
            ]
        },
        2: {
            "rare": ["Pickaxe_ID_032_Tactical"],
            "super_rare": [
                "Pickaxe_ID_025_Dragon", "Pickaxe_ID_019_Heart",
                "Pickaxe_ID_024_Plunger", "Pickaxe_ID_023_SkiBoot",
                "Pickaxe_ID_040_Pizza", "Pickaxe_ID_042_CircuitBreaker", 
                "Pickaxe_ID_038_Carrot", "Pickaxe_ID_037_Stealth", 
                "Pickaxe_ID_034_RockerPunk", "Pickaxe_ID_036_CuChulainn", 
                "Pickaxe_ID_035_Prismatic", "Pickaxe_ID_030_ArtDeco"
            ],
            "epic": ["Pickaxe_ID_043_OrbitingPlanets", "Pickaxe_ID_041_PajamaParty", 
                     "Pickaxe_ID_033_PotOfGold", "Pickaxe_ID_031_Squeak", 
                     "Pickaxe_ID_026_Brite"]
        },
        6: {
            "rare": [
                "Pickaxe_ID_118_StreetOps", "Pickaxe_ID_125_Moth", "Pickaxe_ID_123_HornedMask",
                "Pickaxe_ID_124_Feathers", "Pickaxe_ID_095_FootballTrophy", "Pickaxe_ID_096_FootballReferee",
                "Pickaxe_ID_119_AnimalJackets", "Pickaxe_ID_101_Octoberfest"
            ],
            "super_rare": [
                "Pickaxe_ID_112_GuanYu", "Pickaxe_ID_121_RobotRed", "Pickaxe_ID_120_SamuraiUltraArmor",
                "Pickaxe_ID_122_Witch", "Pickaxe_ID_107_HalloweenTomato", "Pickaxe_ID_094_Football",
                "Pickaxe_ID_117_MadCommander", "Pickaxe_ID_111_BlackWidow", "Pickaxe_ID_108_PumpkinSlice",
                "Pickaxe_ID_107_Plague", "Pickaxe_ID_100_DieselPunk"
            ],
            "epic": [
                "Pickaxe_ID_113_Muertos", "Pickaxe_ID_115_EvilCowboy", "Pickaxe_ID_110_Vampire",
                "Pickaxe_ID_109_SkullTrooper"
            ]
        },
        8: {
            "rare": [
                "Pickaxe_ID_201_Swashbuckler", "Pickaxe_ID_194_TheBomb",
                "Pickaxe_ID_197_HoppityHeist", "Pickaxe_ID_198_BountyBunny",
                "Pickaxe_ID_190_GolfClub", "Pickaxe_ID_183_BaseballBat2018",
                "Pickaxe_ID_172_BandageNinja", "Pickaxe_ID_175_Tropical",
                "Pickaxe_ID_168_Bandolier", "Pickaxe_ID_171_OrangeCamo"
            ],
            "super_rare": [
                "Pickaxe_ID_179_StarWand", "Pickaxe_ID_204_Miner",
                "Pickaxe_ID_199_ShinyHammer", "Pickaxe_ID_196_EvilBunny",
                "Pickaxe_ID_192_PalmTree", "Pickaxe_ID_191_Banana",
                "Pickaxe_ID_182_PirateWheel", "Pickaxe_ID_185_BadassCowboyCactus",
                "Pickaxe_ID_184_DarkShaman", "Pickaxe_ID_181_Log",
                "Pickaxe_ID_173_SciOps", "Pickaxe_ID_180_TriStar",
                "Pickaxe_ID_174_LuckyRider", "Pickaxe_ID_170_Aztec",
                "Pickaxe_ID_169_Farmer"
            ],
            "epic": [
                "Pickaxe_ID_200_MoonlightAssassin", "Pickaxe_ID_186_DemonStone",
                "Pickaxe_ID_127_Rhino", "Pickaxe_ID_176_DevilRock"
            ]
        }
    }

    pickaxes_battlepass_by_season = {
        2: {
            "epic": ["Pickaxe_ID_013_Teslacoil"],
            "super_rare": ["Pickaxe_ID_012_District", "Pickaxe_ID_011_Medieval"]
        },
        6: {
            "super_rare": [
                "Pickaxe_ID_103_FortniteDJ", "Pickaxe_ID_102_RedRiding"
            ]
        },
        8: {
            "epic": ["Pickaxe_ID_200_MoonlightAssassin"],
            "super_rare": ["Pickaxe_ID_167_Medusa", "Pickaxe_ID_165_MasterKey"]
        }
    }

    print("Combining items from all seasons up to the current season...")
    combined_items = {"rare": [], "super_rare": [], "epic": [], "legendary": []}
    combined_bp_items = {"rare": [], "super_rare": [], "epic": [], "legendary": []}
    combined_exclusive_items = {"rare": [], "super_rare": [], "epic": [], "legendary": []}
    
    for season in range(1, current_season + 1):
        if season in skins_by_season:
            for rarity, items in skins_by_season[season].items():
                combined_items[rarity].extend(items)
        if include_battle_pass and season in skins_battlepass_by_season:
            for rarity, items in skins_battlepass_by_season[season].items():
                combined_bp_items[rarity].extend(items)
        if season in emotes_by_season:
            for rarity, items in emotes_by_season[season].items():
                combined_items[rarity].extend(items)
        if season in pickaxes_by_season:
            for rarity, items in pickaxes_by_season[season].items():
                combined_items[rarity].extend(items)
        if include_battle_pass and season in pickaxes_battlepass_by_season:
            for rarity, items in pickaxes_battlepass_by_season[season].items():
                combined_bp_items[rarity].extend(items)

    if include_battle_pass:
        for rarity in combined_bp_items:
            combined_items[rarity].extend(combined_bp_items[rarity])
    
    if include_exclusives:
        for rarity, items in exclusive_items.items():
            combined_exclusive_items[rarity].extend(items)

    print("Selecting featured items...")
    used_items = set()
    featured_items = {}

    if more_accurate:
        selected_season = random.choice(list(paired_featured_items.keys()))
        selected_pair = random.choice(paired_featured_items[selected_season])
        featured_items["featured1"] = selected_pair[0]
        featured_items["featured2"] = selected_pair[1]
    else:
        featured_items["featured1"] = ensure_non_none_items(2, "AthenaCharacter", used_items, combined_items)
        featured_items["featured2"] = ensure_non_none_items(2, "AthenaCharacter", used_items, combined_items)

    print("Featured items selected: ", featured_items)

    print("Selecting daily items...")
    daily_items = {
        "daily1": ensure_non_none_items(1, "AthenaDance", used_items, combined_items)[0],
        "daily2": ensure_non_none_items(1, "AthenaPickaxe", used_items, combined_items)[0],
        "daily3": ensure_non_none_items(1, "AthenaCharacter", used_items, combined_items)[0],
        "daily4": ensure_non_none_items(1, "AthenaPickaxe", used_items, combined_items)[0],
        "daily5": ensure_non_none_items(1, "AthenaDance", used_items, combined_items)[0],
        "daily6": ensure_non_none_items(1, "AthenaDance", used_items, combined_items)[0]
    }

    print("Daily items selected: ", daily_items)

    all_items = {**daily_items, **featured_items}
    shop.update(add_items(all_items, combined_items, backbling_mapping))

    print("\nThe BR Item Shop Config is as follows:")
    print("{")
    print('    "//": "BR Item Shop Config",')
    for i, (category, data) in enumerate(shop.items()):
        print(f'    "{category}": {{')
        print(f'        "itemGrants": {data["itemGrants"]},')
        print(f'        "price": {data["price"]}')
        if i < len(shop) - 1:
            print("    },")
        else:
            print("    }")
    print("}")

    featured_images = {
        "CID_107_Athena_Commando_F_PajamaParty": "https://fortnite.gg/img/items/820/featured.png?2",
        "CID_093_Athena_Commando_M_Dinosaur": "https://fortnite.gg/img/items/834/featured.png?1",
        "CID_104_Athena_Commando_F_Bunny": "https://fortnite.gg/img/items/823/featured.png?2",
        "CID_103_Athena_Commando_M_Bunny": "https://fortnite.gg/img/items/824/featured.png?2",
        "CID_097_Athena_Commando_F_RockerPunk": "https://fortnite.gg/img/items/830/featured.png?1",
        "CID_268_Athena_Commando_M_RockerPunk": "https://fortnite.gg/img/items/661/featured.png?2",
        "CID_123_Athena_Commando_F_Metal": "https://fortnite.gg/img/items/804/featured.png?2",
        "CID_122_Athena_Commando_M_Metal": "https://fortnite.gg/img/items/805/featured.png?2",
        "CID_135_Athena_Commando_F_Jailbird": "https://fortnite.gg/img/items/792/featured.png?1",
        "CID_134_Athena_Commando_M_Jailbird": "https://fortnite.gg/img/items/793/featured.png?2",
        "CID_154_Athena_Commando_M_Gumshoe": "https://fortnite.gg/img/items/773/featured.png?2",
        "CID_155_Athena_Commando_F_Gumshoe": "https://fortnite.gg/img/items/772/featured.png?2",
        "CID_124_Athena_Commando_F_AuroraGlow": "https://fortnite.gg/img/items/803/featured.png?1",
        "CID_126_Athena_Commando_M_AuroraGlow": "https://fortnite.gg/img/items/801/featured.png?1",
        "CID_220_Athena_Commando_F_Clown": "https://fortnite.gg/img/items/709/featured.png?2",
        "CID_221_Athena_Commando_M_Clown": "https://fortnite.gg/img/items/708/featured.png?2",
        "CID_192_Athena_Commando_M_Hippie": "https://fortnite.gg/img/items/736/featured.png?2",
        "CID_193_Athena_Commando_F_Hippie": "https://fortnite.gg/img/items/735/featured.png?2",
        "CID_198_Athena_Commando_M_BlueSamurai": "https://fortnite.gg/img/items/730/featured.png?2",
        "CID_199_Athena_Commando_F_BlueSamurai": "https://fortnite.gg/img/items/729/featured.png?2",
        "CID_328_Athena_Commando_F_Tennis": "https://fortnite.gg/img/items/610/featured.png?2",
        "CID_334_Athena_Commando_M_Scrapyard": "https://fortnite.gg/img/items/604/featured.png?2",
        "CID_297_Athena_Commando_F_Math": "https://fortnite.gg/img/items/638/featured.png?2",
        "CID_296_Athena_Commando_M_Math": "https://fortnite.gg/img/items/639/icon.png?5",
        "CID_345_Athena_Commando_M_LoveLlama": "https://fortnite.gg/img/items/593/featured.png?2",
        "EID_KissKiss": "https://fortnite.gg/img/items/3863/featured.png?1",
        "CID_398_Athena_Commando_M_TreasureHunterFashion": "https://fortnite.gg/img/items/544/featured.png?1",
        "CID_397_Athena_Commando_F_TreasureHunterFashion": "https://fortnite.gg/img/items/545/featured.png?1",
        "CID_394_Athena_Commando_M_MoonlightAssassin": "https://fortnite.gg/img/items/548/featured.png?1",
        "CID_395_Athena_Commando_F_ShatterFly": "https://fortnite.gg/img/items/547/featured.png?2",
        "CID_372_Athena_Commando_F_Pirate01": "https://fortnite.gg/img/items/567/featured.png?2",
        "CID_373_Athena_Commando_M_Pirate01": "https://fortnite.gg/img/items/566/featured.png?2",
        "CID_358_Athena_Commando_M_Aztec": "https://fortnite.gg/img/items/580/featured.png?1",
        "CID_359_Athena_Commando_F_Aztec": "https://fortnite.gg/img/items/579/featured.png?1",
        "CID_355_Athena_Commando_M_Farmer": "https://fortnite.gg/img/items/583/featured.png?1",
        "CID_356_Athena_Commando_F_Farmer": "https://fortnite.gg/img/items/582/featured.png?1",
        "CID_392_Athena_Commando_F_BountyBunny": "https://fortnite.gg/img/items/550/featured.png?1",
        "CID_391_Athena_Commando_M_HoppityHeist": "https://fortnite.gg/img/items/551/featured.png?2"
    }

    save_to_file(shop)
    generate_html(shop, featured_images)

    if webhook_url:
        send_to_discord(webhook_url, shop)

    print("Script execution completed.")

if __name__ == "__main__":
    include_battle_pass = False
    include_exclusives = False
    webhook_url = "https://discord.com/api/webhooks/1299010730191880245/k1LhaNt815gbGWCJddXaBEUtmiewA3ZAcT8n7BZkRbwLfuvflOHeOGvv7LHl6DX-yt-o"
    more_accurate = True

    main(include_battle_pass, include_exclusives, webhook_url, more_accurate)